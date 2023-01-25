import asyncio
import time
from collections import OrderedDict
from typing import Dict, Set

import zmq
import zmq.asyncio

from .protocol import HEARTBEAT, READY


class Broker:
    def __init__(self,
                 manager_address,
                #  frontend_address,
                 backend_address,
                #  publish_address,
                #  subscribe_address,
                 heartbeat_interval_s: int = 1,
                 heartbeat_timeout_s: int = 3,
                 heartbeat_liveness: int = 3,):
        self._heartbeat_interval_s = heartbeat_interval_s
        self._heartbeat_timeout_s = heartbeat_timeout_s
        self._heartbeat_liveness = heartbeat_liveness
        self._manager_liveness = heartbeat_liveness

        self._kill = asyncio.Event()

        self._context = zmq.asyncio.Context()

        # self._mgr_request_socket = self._context.socket(zmq.REQ)
        self._mgr_hearbeat_socket = self._context.socket(zmq.ROUTER)
        self._mgr_hearbeat_socket.bind(manager_address)

        self._mgr_heartbeat_poller = zmq.asyncio.Poller()
        self._mgr_heartbeat_poller.register(self._mgr_hearbeat_socket, zmq.POLLIN)

        # self._frontend_socket = self._context.socket(zmq.ROUTER)
        # self._frontend_socket.bind(frontend_address)

        self._backend_socket = self._context.socket(zmq.ROUTER)
        self._backend_socket.bind(backend_address)

        # self._frontend_poller = zmq.asyncio.Poller()
        # self._frontend_poller.register(self._frontend_socket, zmq.POLLIN)

        self._backend_poller = zmq.asyncio.Poller()
        self._backend_poller.register(self._backend_socket, zmq.POLLIN)

        self._lock = asyncio.Lock()
        self._workers: Set[int] = set()
        self._worker_liveness: Dict[str, int] = {}
        self._worker_last_seen: Dict[str, int] = {}

    async def _send_heartbeat(self):
        """Periodically sends heartbeats to workers"""
        heartbeat_at = time.time() + self._heartbeat_interval_s

        while not self._kill.is_set():
            if time.time() > heartbeat_at:
                for worker in self._workers:
                    msg = [worker, HEARTBEAT]
                    self._backend_socket.send_multipart(msg)

                heartbeat_at = time.time() + self._heartbeat_interval_s
            await asyncio.sleep(5e-2)

    async def _handle_manager_heartbeat(self):
        """Periodically sends heatbeats to manager and waits for
        heartbeats from manager. Manager is critical, so interchange
        dies if manager is unresponsive.
        """
        heartbeat_at = time.time() + self._heartbeat_interval_s
        while True:
            socks = await self._mgr_heartbeat_poller.poll(self._heartbeat_timeout_s * 1000)
            socks = dict(socks)

            if socks.get(self._mgr_hearbeat_socket) == zmq.POLLIN:
                frames = await self._mgr_hearbeat_socket.recv_multipart()

                msg = frames[1:]

                if len(msg) == 1 and msg[0] == HEARTBEAT:
                    print("Receved manager heartbeat")
                    self._manager_liveness = self._heartbeat_liveness
                else:
                    self._kill.set()
                    break

            else:
                print("Missed manager heartbeat")
                self._manager_liveness -= 1

                if self._manager_liveness == 0:
                    self._kill.set()
                    break

            if time.time() >= heartbeat_at:
                msg = [b"manager", HEARTBEAT]
                self._mgr_hearbeat_socket.send_multipart(msg)

    async def _handle_backend(self):
        """Handles messages from workers"""
        while not self._kill.is_set():
            print("HERE")
            socks = await self._backend_poller.poll(self._heartbeat_timeout_s * 1000)
            socks = dict(socks)

            if socks.get(self._backend_socket) == zmq.POLLIN:
                frames = await self._backend_socket.recv_multipart()

                address = frames[0]
                msg = frames[1:]

                if len(msg) == 1:
                    if msg[0] == READY:
                        self._workers.add(address)
                        self._worker_liveness[address] = self._heartbeat_liveness
                        self._worker_last_seen[address] = time.time()
                        print(f"Registered {address}")
                        # Send message to manager to start process, await response
                    elif msg[0] == HEARTBEAT:
                        # print(f"Received heartbeat from {address} at {time.time()}")
                        self._worker_last_seen[address] = time.time()
            else:
                print("NO MESSAGE")

            killed_workers = []
            for worker in self._workers:
                if time.time() - self._worker_last_seen[worker] > self._heartbeat_timeout_s:
                    self._worker_liveness[worker] -= 1
                    self._worker_last_seen[worker] = time.time()
                    print(f"Missed heartbeat from {worker}")
                    # print(f"Last seen at {self._worker_last_seen[worker]} currently {time.time()}")

                if self._worker_liveness[worker] == 0:
                    print(f"{worker} dead")
                    killed_workers.append(worker)
                    self._worker_liveness.pop(worker)
                    self._worker_last_seen.pop(worker)

            async with self._lock:
                for worker in killed_workers:
                    self._workers.remove(worker)

    # async def _handle_frontend(self):
    #     while True:
    #         await self._frontend_socket.recv_multipart()
            
    #         if not frames:
    #             continue

    #         address = frames[0]
    #         msg = frames[1:]

    #         # 

    async def _run_async(self):
        self._tasks = [
            asyncio.create_task(self._send_heartbeat()),
            asyncio.create_task(self._handle_backend()),
            asyncio.create_task(self._handle_manager_heartbeat())

        ]

        await asyncio.gather(*self._tasks)

    def run(self):
        asyncio.run(self._run_async())


def main():
    w = Broker("tcp://*:5557", "tcp://*:5556")
    w.run()