import logging
import multiprocessing
import os
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Optional
import asyncio
import zmq
import zmq.asyncio
from .. import protocol
import json
import redis
import redis.asyncio

# from .process_managers.backtest_manager import BacktestManager
from .process_managers.web_socket_manager import WebSocketManager

logger = logging.getLogger(__name__)

__all__ = ('Manager',)


class Manager:
    # Manager sends heartbeats to interchange and also receives tasks from frontend from interchange to handle
    """Manages the startup and status/state of worker processes"""
    def __init__(self,
                 manager_uuid,
                 broker_uuid,
                 broker_address,
                 worker_address,
                 redis_host,
                 redis_port,
                 num_threads=5,
                 max_processes=multiprocessing.cpu_count() - 2,
                 heartbeat_interval_s: int = 1,
                 heartbeat_timeout_s: int = 3,
                 heartbeat_liveness: int = 3):
        self._kill = asyncio.Event()

        self._manager_uuid = manager_uuid
        self._broker_uuid = broker_uuid

        self._num_threads = num_threads
        self._max_processes = max_processes

        self._heartbeat_interval_s = heartbeat_interval_s
        self._heartbeat_timeout_s = heartbeat_timeout_s
        self._heartbeat_liveness = heartbeat_liveness

        # Initialize socket connections
        self._context = zmq.asyncio.Context()

        self._mgr_be = self._context.socket(zmq.DEALER)
        self._mgr_be.connect(broker_address)
        self._mgr_be_poller = zmq.asyncio.Poller()
        self._mgr_be_poller.register(self._mgr_be, zmq.POLLIN)

        self._worker_fe = self._context.socket(zmq.DEALER)
        self._worker_fe.connect(worker_address)

        # Initialize redis
        self._redis_host = redis_host
        self._redis_port = redis_port

        self._redis_conn = redis.Redis(host=self._redis_host, port=self._redis_port)
        self._redis_conn.set("num_workers", 0)
        self._redis_conn.close()

        self._redis_conn = redis.asyncio.Redis(host=self._redis_host, port=self._redis_port)

        self._web_socket_manager = WebSocketManager(self)
        # self._backtest_manager = BacktestManager(self)

    async def _handle_worker_socket(self):
        """Listens for status updates from workers and updates status on redis.
        """
        while not self._kill.is_set():
            frames = await self._worker_fe.recv_multipart()

            if not frames:
                continue

            msg = frames[1:]

            if len(msg) != 3:
                continue

            worker_address = msg[0]
            status = msg[1]
            status_details = msg[2]

            if await self._redis_conn.exists(worker_address):
                entry = await self._redis_conn.get(worker_address)
                entry = json.loads(entry)

                entry["status"] = status
                entry["status_details"] = status_details

                await self._redis_conn.set(worker_address, entry)

    async def _handle_client_socket(self):
        while not self._kill.is_set():
            frames = await self._mgr_be.recv_multipart()

            if not frames:
                continue

            res = self._validate_client_message(frames)

            if not res:
                continue

            address, service_type, command, params = res

            match service_type:
                case b"websocket":
                    await self.web_sockets._consume_message(address, command, params)
                case b"backtest":
                    await self.backtest._consume_message(address, command, params)
                case _:
                    msg = [address, protocol.ERROR, b"Invalid service"]
                    await self._mgr_be.send_multipart(msg)

    def _async_run(self):
        self._tasks = [self._consume_messages() for _ in range(self._num_threads)]

        asyncio.gather(*self._tasks)

    def shutdown(self):
        """Deallocates all necessary resources. No manager operations
        should be done after calling this function."""
        self.web_sockets.shutdown()
        self.backtest.shutdown()

    @property
    def web_sockets(self) -> WebSocketManager:
        """Provides access to web sockets"""
        return self._web_socket_manager

    # @property
    # def backtest(self) -> BacktestManager:
    #     """Provides access to backtest"""
    #     return self._backtest_manager


def main():
    m = Manager("manager", "broker", "tcp://localhost:5558", "tcp://localhost:5556",
    "localhost", 6379)