import asyncio
import time
from typing import Dict, Set

import zmq
import zmq.asyncio
import threading

from . import protocol
import argparse
import subprocess
from .utils import convert_tcp_address

class Broker:
    # Client talks to frontend, frontend is fowarded to manager, manager talks to backend
    def __init__(self,
                 broker_uuid: str,
                 manager_uuid: str,
                 manager_address: str,
                 frontend_address: str,
                 backend_address: str,
                 publish_address: str,
                 subscribe_address: str,
                 redis_host: str,
                 redis_port: str,
                 heartbeat_interval_s: int = 1,
                 heartbeat_timeout_s: int = 3,
                 heartbeat_liveness: int = 3,):
        self._broker_uuid = broker_uuid.encode()
        self._manager_uuid = manager_uuid.encode()
        self._heartbeat_interval_s = heartbeat_interval_s
        self._heartbeat_timeout_s = heartbeat_timeout_s
        self._heartbeat_liveness = heartbeat_liveness
        self._manager_liveness = heartbeat_liveness

        self._redis_host = redis_host
        self._redis_port = redis_port

        # Initialize sockets and connections
        self._manager_address = manager_address
        self._backend_address = backend_address
        self._frontend_address = frontend_address
        self._publish_address = publish_address
        self._subscribe_address = subscribe_address

        self._context = zmq.asyncio.Context()

        # Receives messages from clients
        self._client_fe = self._context.socket(zmq.ROUTER)
        self._client_fe.bind(frontend_address)

        # Gets forwarded client messages and receives manager mesages
        self._mgr_fe = self._context.socket(zmq.ROUTER)
        self._mgr_fe.bind(manager_address)

        self._mgr_fe_poller = zmq.asyncio.Poller()
        self._mgr_fe_poller.register(self._mgr_fe, zmq.POLLIN)

        # Sends messages to workers and receives worker responses
        self._worker_be = self._context.socket(zmq.ROUTER)
        self._worker_be.bind(backend_address)

        # Pub/sub for financial data
        self._xsub = self._context.socket(zmq.XSUB)
        self._xsub.bind(self._publish_address)

        self._xpub = self._context.socket(zmq.XPUB)
        self._xpub.bind(self._subscribe_address)

        # Polls workers
        self._worker_be_poller = zmq.asyncio.Poller()
        self._worker_be_poller.register(self._worker_be, zmq.POLLIN)

        self._lock = asyncio.Lock()
        self._workers: Set[int] = set()
        self._worker_liveness: Dict[str, int] = {}
        self._worker_last_seen: Dict[str, int] = {}

        self._kill = asyncio.Event()

    async def _start_manager(self):
        """Starts manager in separate subprocess and waits for it to connect to
        the manager frontend socket and the worker backend socket

        Raises
        ------
        ValueError
            Raises error if manager times out and doesn't connect in time
        """
        manager_cmd = (
            "manager "
            f"--manager-uuid={self._manager_uuid.decode()} "
            f"--broker-uuid={self._broker_uuid.decode()} "
            f"--broker-address={convert_tcp_address(self._manager_address)} "
            f"--worker-address={convert_tcp_address(self._backend_address)} "
            f"--redis-host={self._redis_host} "
            f"--redis-port={self._redis_port} "
        )

        subprocess.Popen(manager_cmd.split(), shell=False, start_new_session=True)

        mgr_startup_poller = zmq.asyncio.Poller()
        mgr_startup_poller.register(self._mgr_fe, zmq.POLLIN)
        mgr_startup_poller.register(self._worker_be, zmq.POLLIN)

        # Check to make sure manager is ready
        mgr_ready = 0
        timeout_count = 5
        while timeout_count:
            socks = await mgr_startup_poller.poll(self._heartbeat_timeout_s * 1000)
            socks = dict(socks)

            if socks.get(self._mgr_fe) == zmq.POLLIN:
                frames = await self._mgr_fe.recv_multipart()

                if len(frames) == 2:
                    address = frames[0]

                    if address == self._manager_uuid and frames[1] == protocol.READY:
                        mgr_ready += 1

            if socks.get(self._worker_be) == zmq.POLLIN:
                frames = await self._worker_be.recv_multipart()

                if len(frames) == 2:
                    address = frames[0]

                    if address == self._manager_uuid and frames[1] == protocol.READY:
                        mgr_ready += 1

            if not socks:
                timeout_count -= 1

            if mgr_ready == 2:
                return

        raise ValueError("Failed to start manager")

    async def _manage_client_fe(self):
        """Forwards messages from client facing front end to manager. A valid client
        message consists of the following:

        1. Client address: identity of client socket initiating request 
        (automatically added to message by REQ socket)
        2. Empty frame: empty frame denoting beginning of message content
        (automatically added to message by REQ socket)
        3. Service type: the type of service to interface with as a byte string
        (such as "websocket" or "backtest")
        4. Command: the command to provide to the service as a byte string (such
        as "start" or "stop")
        5. Params: parameters to pass to the command as a json dumped byte string

        This function rearranges the frames into the following format:
        1. Manager address: identity of manager to send client message to
        (automatically stripped by ROUTER socket)
        2. Client address: the identity of the client's socket as a byte string
        3. Service type: the type of service to interface with as a byte string
        (such as "websocket" or "backtest")
        4. Command: the command to provide to the service as a byte string (such
        as "start" or "stop")
        5. Params: parameters to pass to the command as a json dumped byte string
        """
        while not self._kill.is_set():
            print("_manager_client_fe")
            frames = await self._client_fe.recv_multipart()
            print(f"RECEIVED FROM CLIENT: {frames}")
            client_address = frames[0]
            client_msg = frames[2:]

            msg = [self._manager_uuid, client_address] + client_msg
            await self._mgr_fe.send_multipart(msg)

    async def _manage_mgr_fe(self):
        """Handles the following tasks:

        1. Periodically send heartbeats to manager
        2. Check for heartbeats from manager. Manager is critical so broker dies if
        manager is unresponsive
        3. Forward messages from the manager back to the client
        """
        heartbeat_at = time.time() + self._heartbeat_interval_s

        while not self._kill.is_set():
            print("_manager_mgr_fe")
            socks = await self._mgr_fe_poller.poll(self._heartbeat_timeout_s * 1000)
            socks = dict(socks)

            if socks.get(self._mgr_fe) == zmq.POLLIN:
                frames = await self._mgr_fe.recv_multipart()

                if not frames:
                    self._kill.set()
                    break

                address = frames[0]

                if address != self._manager_uuid:
                    continue

                msg = frames[1:]
                print(msg)

                # Check if heartbeat
                if len(msg) == 1 and msg[0] == protocol.HEARTBEAT:
                    print("Receved manager heartbeat")
                    self._manager_liveness = self._heartbeat_liveness
                else:
                    # Forward message to client
                    print(f"RECEIVED FROM MANAGER: {frames}")
                    client_address = msg[1]
                    msg_content = msg[1:]
                    msg = [client_address, b''] + msg_content
                    print(f"Sending to client: {msg}")
                    await self._client_fe.send_multipart(msg)
            else:
                print("Missed manager heartbeat")
                self._manager_liveness -= 1

                if self._manager_liveness == 0:
                    self._kill.set()
                    break

            # Send heartbeat
            if time.time() >= heartbeat_at:
                msg = [self._manager_uuid, protocol.HEARTBEAT]
                self._mgr_fe.send_multipart(msg)

                heartbeat_at = time.time() + self._heartbeat_interval_s

        await self._shutdown()

    async def _manage_worker_be(self):
        """Handles the following tasks:

        1. Registers workers
        2. Periodically send heartbeats to workers
        3. Check for heartbeats from workers. If a worker is unresponsive, send a
        message to the manager to update worker status
        4. Forward messages from worker to manager
        """
        heartbeat_at = time.time() + self._heartbeat_interval_s

        while not self._kill.is_set():
            print("_manager_worker_be")
            socks = await self._worker_be_poller.poll(self._heartbeat_timeout_s * 1000)
            socks = dict(socks)

            if socks.get(self._worker_be) == zmq.POLLIN:
                frames = await self._worker_be.recv_multipart()

                worker_address = frames[0]
                msg = frames[1:]

                if len(msg) == 1:
                    # Registers worker
                    if msg[0] == protocol.READY:
                        self._workers.add(worker_address)
                        self._worker_liveness[worker_address] = self._heartbeat_liveness
                        self._worker_last_seen[worker_address] = time.time()
                        print(f"Registered {worker_address}")
                    elif msg[0] == protocol.HEARTBEAT:
                        # Receive heartbeat
                        self._worker_last_seen[worker_address] = time.time()
                    elif msg[0] == protocol.DIE or msg[0] == protocol.STATUS:
                        # Receive critical error and forward to manager
                        status_details = msg[1]
                        msg = [self._manager_uuid, worker_address, msg[0], status_details]
                        await self._worker_be.send_multipart(msg)

            killed_workers = []
            for worker in self._workers:
                if time.time() - self._worker_last_seen[worker] > self._heartbeat_timeout_s:
                    self._worker_liveness[worker] -= 1
                    self._worker_last_seen[worker] = time.time()
                    print(f"Missed heartbeat from {worker}")
                    # print(f"Last seen at {self._worker_last_seen[worker]} currently {time.time()}")

                # Kill worker
                if self._worker_liveness[worker] == 0:
                    print(f"Killing {worker}")
                    killed_workers.append(worker)
                    self._worker_liveness.pop(worker)
                    self._worker_last_seen.pop(worker)

                    msg = [worker, protocol.DIE]
                    await self._worker_be.send_multipart(msg)

                    msg = [self._manager_uuid, worker_address, protocol.DIE, b"timeout"]
                    await self._mgr_fe.send_multipart(msg)

            for worker in killed_workers:
                self._workers.remove(worker)

            if time.time() >= heartbeat_at:
                for worker in self._workers:
                    msg = [worker, protocol.HEARTBEAT]
                    self._worker_be.send_multipart(msg)

                    heartbeat_at = time.time() + self._heartbeat_interval_s

    async def _run_async(self):
        await self._start_manager()

        proxy_thread = threading.Thread(target=zmq.proxy, 
                                        args=(self._xsub, self._xpub), 
                                        daemon=True)
        proxy_thread.start()

        self._tasks = [
            asyncio.create_task(self._manage_client_fe()),
            asyncio.create_task(self._manage_mgr_fe()),
            # asyncio.create_task(self._manage_worker_be()),
            # asyncio.create_task(self._manage_client_be())
        ]
        try:
            await asyncio.gather(*self._tasks)
        except asyncio.CancelledError:
            return

    async def _shutdown(self):
        self._client_fe.setsockopt(zmq.LINGER, 0)
        self._mgr_fe.setsockopt(zmq.LINGER, 0)
        self._worker_be.setsockopt(zmq.LINGER, 0)
        self._xpub.setsockopt(zmq.LINGER, 0)
        self._xsub.setsockopt(zmq.LINGER, 0)

        self._client_fe.close()
        self._mgr_fe.close()
        self._worker_be.close()
        self._xpub.close()
        self._xsub.close()

        self._context.term()

        for task in self._tasks:
            task.cancel()

    def run(self):
        asyncio.run(self._run_async())

def cli_run():
    """

    broker --broker-uuid="broker" --manager-uuid="manager" --manager-address="tcp://127.0.0.1:5558" --frontend-address="tcp://127.0.0.1:5557" --backend-address="tcp://127.0.0.1:5556" --publish-address="tcp://127.0.0.1:5559" --subscribe-address="tcp://127.0.0.1:6000" --redis-host="localhost" --redis-port=6379

    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--broker-uuid", required=True,
        help="uuid of broker"
    )

    parser.add_argument(
        "--manager-uuid", required=True,
        help="uuid of manager"
    )

    parser.add_argument(
        "--manager-address", required=True,
        help="address to bind manager socket"
    )

    parser.add_argument(
        "--frontend-address", required=True,
        help="address to bind frontend socket"
    )

    parser.add_argument(
        "--backend-address", required=True,
        help="address to bind backend socket"
    )

    parser.add_argument(
        "--publish-address", required=True,
        help="address to bind xsub socket"
    )

    parser.add_argument(
        "--subscribe-address", required=True,
        help="address to bind spub socket"
    )

    parser.add_argument(
        "--redis-host", required=True,
        help="host of redis server to use"
    )

    parser.add_argument(
        "--redis-port", required=True, type=int,
        help="port of redis server"
    )

    parser.add_argument(
        "--heartbeat-interval-s", required=False, type=int,
        default=1, help="uuid of interchange"
    )

    parser.add_argument(
        "--heartbeat-timeout-s", required=False, type=int,
        default=3, help="uuid of interchange"
    )

    parser.add_argument(
        "--heartbeat-liveness", required=False, type=int,
        default=3, help="uuid of interchange"
    )

    args = parser.parse_args()

    # pub_sub_ports = None
    # if isinstance(args.pub_sub_ports, str):
    #     pub_str, sub_str = args.pub_sub_ports.split(",")
    #     pub_sub_ports = (int(pub_str), int(sub_str))
    # else:
    #     pub_sub_ports = args.pub_sub_ports

    broker = Broker(
        args.broker_uuid,
        args.manager_uuid,
        args.manager_address,
        args.frontend_address,
        args.backend_address,
        args.publish_address,
        args.subscribe_address,
        args.redis_host,
        args.redis_port,
        heartbeat_interval_s=args.heartbeat_interval_s,
        heartbeat_timeout_s=args.heartbeat_timeout_s,
        heartbeat_liveness=args.heartbeat_liveness
    )

    broker.run()

def main():
    w = Broker("broker", "manager", "tcp://127.0.0.1:5558", "tcp://127.0.0.1:5557", "tcp://127.0.0.1:5556",
               "localhost", 6379)
    w.run()