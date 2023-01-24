import argparse
import asyncio
from typing import List
import zmq
import zmq.asyncio

from ...data_acquisition.websocket_consumers.websocket_consumer_factory import WebsocketConsumerFactory
from ...data_acquisition.ccxt_websocket import CCXTWebSocket


class WebSocketWorker:
    """Worker class for running a producer/consumer for
    web sockets.
    """
    def __init__(self,
                 worker_uuid,
                 exchange: str,
                 tickers: List[str], 
                 consumer_name: str,
                 broker_address: str,
                 heartbeat_interval: int = 30 * 1000,
                 heartbeat_liveness = 3,
                 **kwargs):
        """Creates a worker to run a web socket.

        Parameters
        ----------
        address : _type_
            _description_
        port : _type_
            _description_
        """
        self._worker_uuid = worker_uuid
        self._tickers = tickers

        # Web socket initialization
        consumer_factory = WebsocketConsumerFactory()
        consumer = consumer_factory.get(consumer_name)
        consumer = consumer(kwargs)

        self._web_socket = CCXTWebSocket(exchange, tickers, consumer)

        # Hearbeat initialization
        self._heartbeat_interval = heartbeat_interval
        self._heartbeat_liveness = heartbeat_liveness

        context = zmq.asyncio.context()
        self._broker_socket = context.socket(zmq.DEALER)
        self._broker_socket.setsockopt(zmq.IDENTITY, b"{self._worker_uuid}")
        self._poller = zmq.asyncio.Poller()
        self._poller.register(self._broker_socket, zmq.POLLIN)
        self._broker_socket.connect(broker_address)
        self.send(b"READY")

    async def _manage_broker(self):
        """Polls socket for incoming messages. There are two types of 
        messages:

        1. Heartbeat: Replies to broker with heartbeat. If too many 
        heartbeats are missed, assume broker is dead and die.
        2. Kill: Begins shutdown process and sends acknowledgement 
        to broker.
        """
        liveness = self._heartbeat_liveness

        while True:
            socks = await self._poller.poll(self._heartbeat_interval)
            socks = dict(socks)

            if socks.get(self._broker_socket) == zmq.POLLIN:
                frames = await self._broker_socket.recv_multipart()

                if not frames:
                    self._cancel()
                    break

                if len(frames) >= 3 and frames[0] == b"\x02" and frames[2] == b"KILL":
                    self._shutdown()
                elif len(frames) == 1 and frames[0] == b"\x01":
                    liveness = self._heartbeat_liveness
            else:
                liveness -= 1

                if liveness == 0:
                    self._cancel()
                    break


    async def _run_async(self, ml1_queues, ml2_queues, flag):
        """
        Awaits web socket and consumer tasks asynchronously.
        """
        self._ml1_queues = ml1_queues
        self._ml2_queues = ml2_queues

        self._ws_ml1_queue = asyncio.Queue()
        self._ws_ml2_queue = asyncio.Queue()

        self._ccxt_ws = ccxtws("", self._ws_ml1_queue, 
                               self._ws_ml2_queue, 
                               self._tickers)

        self._produce_tasks = [asyncio.create_task(self._ccxt_ws.async_run())]
        self._flag_task = [asyncio.create_task(self.check_flag(flag))]
        self._consume_tasks = [
            asyncio.create_task(self._consume(self._ws_ml1_queue, 
                                              self._ml1_queues)),
            asyncio.create_task(self._consume(self._ws_ml2_queue, 
                                              self._ml2_queues))
        ]

        await asyncio.gather(*self._produce_tasks)

    def run(self, ml1_queue, ml2_queue, flag=None) -> None:
        """
        Wrapper function for starting run_async.
        """
        asyncio.run(self._run_async(ml1_queue, ml2_queue, flag))


def cli_run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tickers", nargs="*", required=True,
        help="Tickers to run in websocket"
    )
    args = parser.parse_args()

    worker = WebSocketWorker(args.tickers)
    worker.run()
