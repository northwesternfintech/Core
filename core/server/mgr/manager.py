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

from .process_managers.backtest_manager import BacktestManager
from .web_socket_manager import WebSocketManager

logger = logging.getLogger(__name__)

__all__ = ('Manager',)


class Manager:
    # Manager sends heartbeats to interchange and also receives tasks from frontend from interchange to handle
    """Manages the startup and status/state of worker processes"""
    def __init__(self,
                 broker_address,
                 worker_address,
                 redis_address,
                 redis_password,
                 num_threads=5,
                 max_processes=multiprocessing.cpu_count() - 2,
                 heartbeat_interval_s: int = 1,
                 heartbeat_timeout_s: int = 3,
                 heartbeat_liveness: int = 3,):
        self._num_threads = num_threads
        self._broker_address = heartbeat_address
        self._broker_socket = broker_address
        
        self._redis_address = redis_address
        self._redis_password = redis_password

        self._max_processes = max_processes

        self._heartbeat_interval_s = heartbeat_interval_s
        self._heartbeat_timeout_s = heartbeat_timeout_s
        self._heartbeat_liveness = heartbeat_liveness

        # Initialize socket connections
        self._context = zmq.asyncio.Context()

        self._broker_socket = self._context.socket(zmq.DEALER)
        self._broker_poller = zmq.asyncio.Poller()
        self._broker_poller.register(self._broker_socket, zmq.POLLIN)

        self._worker_socket = self._context.socket(zmq.DEALER)

        self._web_socket_manager = WebSocketManager(self)
        self._backtest_manager = BacktestManager(self)

        self._kill = asyncio.Event()

    def validate_message(self, frames, service_type):
        if not frames:
            return

        address = frames[0]
        if len(frames) < 4:
            msg = [address, protocol.ERROR, b"Message too short"]
            self._backend_socket.send_multipart(msg)
            return

        service_type = frames[1].decode()
        command = frames[2].decode()
        params = frames[3].decode()

        if frames[1] != service_type:
            msg = [address, protocol.ERROR, b"Invalid service"]
            self._backend_socket.send_multipart(msg)
            return

        try:
            params = json.load(params)
        except:
            msg = [address, protocol.ERROR, b"Failed to load params"]
            self._backend_socket.sent_multipart(msg)
            return

        return address, command, params

    async def _handle_worker_socket(self):
        """Listens for status updates from workers and updates status on redis.
        """
        while not self._kill.is_set():
            frames = await self._worker_socket.recv_multipart()

            if not frames:
                continue

            address = frames[0]

    async def _consume_messages(self):
        while not self._kill.is_set():
            frames = await self._backend_socket.recv_multipart()

            if not frames:
                continue

            address = frames[0]
            
            # Invalid message
            if len(frames) < 2:
                msg = [address, protocol.ERROR, b"Message too short"]
                self._backend_socket.send_multipart(msg)

            service_type = frames[1]
            match service_type:
                case b"websocket":
                    await self.web_sockets._consume_message(frames)
                    break
                case b"backtest":
                    await self.backtest._consume_message(frames)
                    break
                case _:
                    msg = [address, protocol.ERROR, b"Invalid service"]
                    self._backend_socket.send_multipart(msg)

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

    @property
    def backtest(self) -> BacktestManager:
        """Provides access to backtest"""
        return self._backtest_manager

    
        


def main():
    m = Manager()
    u = m.web_sockets.start(["ETH/USDT", "BTC/USDT"])
    print("HERE")
    v = m.backtest.start(mode='live', tickers=['BTC/USDT', 'ETH/USDT'])

    time.sleep(2)
    # m.backtest.stop(v)
    print(m.backtest.status_all())
    # m.web_sockets.stop(u)
    print(m.web_sockets.status_all())