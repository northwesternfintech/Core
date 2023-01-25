import zmq
import zmq.asyncio
import asyncio
import time
from core.data_acquisition.ccxt_websocket import CCXTWebSocket
from typing import List

from core.data_acquisition.websocket_consumers.websocket_consumer_factory import WebsocketConsumerFactory
from .workers.worker import Worker


class WebSocketWorker(Worker):
    """Worker class for running a producer/consumer for
    web sockets
    """
    def __init__(self,
                 exchange: str,
                 tickers: List[str], 
                 publish_addres: str,
                 worker_uuid,
                 broker_address: str,
                 heartbeat_interval_s: int = 1,
                 heartbeat_timeout_s: int = 1, 
                 heartbeat_liveness: int = 3,):
        super().__init__(worker_uuid, 
                         heartbeat_address, 
                         heartbeat_interval_s, 
                         heartbeat_timeout_s)

    async def _handle_broker_messages(self):
        """Polls socket for incoming messages. There are two types of 
        messages:

        1. Heartbeat: Replies to broker with heartbeat. If too many 
        heartbeats are missed, assume broker is dead and die.
        2. Kill: Begins shutdown process and sends acknowledgement 
        to broker.
        """
        liveness = self._heartbeat_liveness
        while not self._kill.is_set():
            print("starting polling!")
            socks = await self._poller.poll(self._heartbeat_timeout_s * 1000)
            socks = dict(socks)

            if socks.get(self._broker_socket) == zmq.POLLIN:
                print("received message!")
                frames = await self._broker_socket.recv_multipart()

                if not frames:
                    print("Received empty frame")
                    self._kill.set()
                    break

                if len(frames) >= 3 and frames[0] == b"\x01" and frames[2] == b"KILL":
                    print("received die")
                    self._shutdown()
                elif len(frames) == 1 and frames[0] == b"\x02":
                    print("received hearbeat")
                    liveness = self._heartbeat_liveness
                else:
                    print(frames)
            else:
                print("received no heartbeat")
                liveness -= 1
                print(f"{liveness} lives left")

                if liveness == 0:
                    self._kill.set()
                    break

        await self._shutdown()

    async def _send_heartbeat(self):
        self._broker_socket.send(b"\x01")
        heartbeat_at = time.time() + self._heartbeat_interval_s

        while not self._kill.is_set():
            if time.time() > heartbeat_at:
                print("Sent heartbeat!")
                self._broker_socket.send(b"\x02")
                heartbeat_at = time.time() + self._heartbeat_interval_s
            await asyncio.sleep(5e-2)

    def _shutdown(self):
        self._broker_socket.setsockopt(zmq.LINGER, 0)
        self._broker_socket.close()

        ws_socket = self._web_socket._ws_consumer._pub_socket
        ws_socket.setsockopt(zmq.LINGER, 0)
        ws_socket.close()

        self._context.term()

        self._web_socket._close()

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
        self._kill = asyncio.Event()

        tasks = self._get_heartbeat_tasks()

        try:
            await asyncio.gather(*tasks)
        except Exception as _:
            return

    def run(self):
        asyncio.run(self._run_async())


def main():
    w = WebSocketWorker(
        "abc123", "kraken", ["BTC/USD"], "tcp://localhost:5556", "tcp://127.0.0.1:50002"
    )
    w.run()