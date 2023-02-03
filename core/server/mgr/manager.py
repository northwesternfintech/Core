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
from .process_managers.websocket_manager import WebSocketManager
from .process_managers.process_manager import ProcessManager

logger = logging.getLogger(__name__)

__all__ = ('Manager',)


class Manager(ProcessManager):
    # Manager sends heartbeats to interchange and also receives tasks from frontend from interchange to handle
    """Manages the startup and status/state of worker processes"""
    def __init__(self,
                 manager_uuid: str,
                 broker_uuid: str,
                 broker_address: str,
                 worker_address: str,
                 redis_host: str,
                 redis_port: int,
                 num_threads=5,
                 max_processes: int = multiprocessing.cpu_count() - 2,
                 heartbeat_interval_s: int = 1,
                 heartbeat_timeout_s: int = 3,
                 heartbeat_liveness: int = 3):
        self._kill = asyncio.Event()

        self._manager_uuid = manager_uuid.encode()
        self._broker_uuid = broker_uuid.encode()

        self._num_threads = num_threads
        self._max_processes = max_processes

        self._heartbeat_interval_s = heartbeat_interval_s
        self._heartbeat_timeout_s = heartbeat_timeout_s
        self._heartbeat_liveness = heartbeat_liveness
        self._heartbeat_at = time.time() + self._heartbeat_interval_s

        # Initialize socket connections
        self._context = zmq.asyncio.Context()

        self._mgr_be = self._context.socket(zmq.DEALER)
        self._mgr_be.setsockopt(zmq.IDENTITY, b"manager")
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

        self._websocket_manager = WebSocketManager(self)
        # self._backtest_manager = BacktestManager(self)

    async def _handle_worker_fe_socket(self):
        """Listens for status updates from workers and updates redis entry.
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

    async def _handle_mgr_be_socket(self):
        """Handles the following tasks:

        1. Periodically send heartbeats to broker
        2. Check for heartbeats from broker
        3. Handles requests from clients
        """
        await self._mgr_be.send_multipart([b"READY"])

        while not self._kill.is_set():
            frames = await self._mgr_be.recv_multipart()

            if not frames:
                continue

            # Handle heartbeat
            if frames[0] == protocol.HEARTBEAT:
                pass
            print(frames)
            # await self._send_client_response(frames[0], [frames[1]])
            # continue
            res = await self._validate_client_message(frames)

            if not res:
                continue

            address, service_type, command, params = res
            # print(res)
            # continue

            match service_type:
                case "websocket":
                    await self.websockets._consume_message(address, command, params)
                case "backtest":
                    await self.backtest._consume_message(address, command, params)
                case _:
                    msg_content = [
                        protocol.ERROR,
                        f"Invalid service type: {service_type}".encode()
                    ]
                    await self._send_client_response(address, msg_content)

    async def _async_run(self):
        # self._tasks = [self._consume_messages() for _ in range(self._num_threads)]
        self._tasks = [self._handle_mgr_be_socket()]

        await asyncio.gather(*self._tasks)

    def run(self):
        asyncio.run(self._async_run())

    def shutdown(self):
        """Deallocates all necessary resources. No manager operations
        should be done after calling this function."""
        self.websockets.shutdown()
        self.backtest.shutdown()

    @property
    def websockets(self) -> WebSocketManager:
        """Provides access to websockets"""
        return self._websocket_manager

    # @property
    # def backtest(self) -> BacktestManager:
    #     """Provides access to backtest"""
    #     return self._backtest_manager


def main():
    m = Manager("manager", "broker", "tcp://localhost:5558", "tcp://localhost:5556",
    "localhost", 6379)
    m.run()