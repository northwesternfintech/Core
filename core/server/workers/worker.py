import asyncio
import time

import zmq
import zmq.asyncio


class Worker:
    """Worker class for running a producer/consumer for
    web sockets.
    """
    def __init__(self,
                 worker_uuid: str,
                 heartbeat_address: str,
                 heartbeat_interval_s: int = 1,
                 heartbeat_timeout_s: int = 1,
                 heartbeat_liveness: int = 3):
        """Worker base class that sends heartbeats to
        broker and listens for hearbeats from broker.

        Parameters
        ----------
        worker_uuid : str
            uuid identifying worker
        heartbeat_address : str
            Address to send heartbeat to. Should include
            transport protocol (e.g. "tcp://127.0.0.1:5000)
        heartbeat_interval_s : int, optional
            Interval (in seconds) to send heartbeat to
            broker, by default 1
        heartbeat_timeout_s : int, optional
            Amount of time to wait for broker heartbeat
            before declaring timeout, by default 1
        heartbeat_liveness : int, optional
            Number of acceptable broker timeouts before 
            dying, by default 3
        """
        self._worker_uuid = worker_uuid

        self._context = zmq.asyncio.Context()

        # Hearbeat initialization
        self._heartbeat_interval_s = heartbeat_interval_s
        self._heartbeat_timeout_s = heartbeat_timeout_s
        self._heartbeat_liveness = heartbeat_liveness

        # Initialize connection with broker
        self._broker_socket = self._context.socket(zmq.DEALER)
        self._broker_socket.setsockopt(zmq.IDENTITY, self._worker_uuid.encode())
        self._poller = zmq.asyncio.Poller()
        self._poller.register(self._broker_socket, zmq.POLLIN)
        self._broker_socket.connect(heartbeat_address)
        self._broker_socket.send(b"\x01")

        self._kill = asyncio.Event()

    async def _handle_broker_messages(self):
        """Polls socket for incoming messages. There are two types of
        messages:

        1. Heartbeat: Replies to broker with heartbeat. If too many
        heartbeats are missed, assume broker is dead and die.
        2. Kill: Begins shutdown process.
        """
        liveness = self._heartbeat_liveness
        while not self._kill.is_set():
            socks = await self._poller.poll(self._heartbeat_timeout_s * 1000)
            socks = dict(socks)

            if socks.get(self._broker_socket) == zmq.POLLIN:
                frames = await self._broker_socket.recv_multipart()

                if not frames:
                    self._kill.set()
                    break

                if len(frames) >= 3 and frames[0] == b"\x01" and frames[2] == b"KILL":
                    self._shutdown()
                elif len(frames) == 1 and frames[0] == b"\x02":
                    liveness = self._heartbeat_liveness
            else:
                liveness -= 1

                if liveness == 0:
                    self._kill.set()
                    break

        await self._shutdown()

    async def _send_heartbeat(self):
        """Periodically sends heartbeats to broker"""
        self._broker_socket.send(b"\x02")
        heartbeat_at = time.time() + self._heartbeat_interval_s

        while not self._kill.is_set():
            if time.time() > heartbeat_at:
                self._broker_socket.send(b"\x02")
                heartbeat_at = time.time() + self._heartbeat_interval_s
            await asyncio.sleep(5e-2)

    def _shutdown(self):
        """Closes connections with broker and stops tasks"""
        self._broker_socket.setsockopt(zmq.LINGER, 0)
        self._broker_socket.close()

        ws_socket = self._web_socket._ws_consumer._pub_socket
        ws_socket.setsockopt(zmq.LINGER, 0)
        ws_socket.close()

        self._context.term()

        for task in self._tasks:
            task.cancel()

    def _get_heartbeat_tasks(self):
        self._tasks = [
            asyncio.create_task(self._handle_broker_messages()),
            asyncio.create_task(self._send_heartbeat()),
            asyncio.create_task(self._web_socket._run_async())
        ]

        return self._tasks

    async def _run_async(self):
        """
        Awaits web socket and consumer tasks asynchronously.
        """
        tasks = self._get_heartbeat_tasks()

        try:
            await asyncio.gather(*tasks)
        except asyncio.exceptions.CancelledError:
            return
        except Exception as e:
            raise e

    def run(self):
        asyncio.run(self._run_async())
