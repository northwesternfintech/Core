import argparse
import asyncio
import json
import os
import signal
from typing import List

from aio_pika import DeliveryMode, ExchangeType, Message, connect
import zmq

from .coinbase import CoinbaseWebSocket


class WebSocketWorker:
    """Worker class for running a producer/consumer for
    web sockets.
    """
    def __init__(self, address, port, tickers: List[str]):
        """Creates a worker to run a web socket.

        Parameters
        ----------
        address : _type_
            _description_
        port : _type_
            _description_
        """
        self._address = address
        self._port = port
        self._tickers = tickers
        self._ticker_exchanges = {}
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.bind("tcp://*:5556")

    async def _consume(self, queue):
        """Consumes data from a queue and pushes it to a broker.

        Parameters
        ----------
        queue : asyncio.Queue
            Queue to consume from.
        """
        while True:
            data = await queue.get()
            queue.task_done()

            message = f"{data['ticker']} {json.dumps(data)}"
            self._socket.send_string(message)

    async def _run_async(self):
        """
        Awaits web socket and consumer tasks asynchronously.
        """
        ml1_queue = asyncio.Queue()
        ml2_queue = asyncio.Queue()

        cwr = CoinbaseWebSocket(ml1_queue, ml2_queue, self._tickers)

        tasks = [asyncio.create_task(cwr._run()),
                #  asyncio.create_task(self._consume(ml1_queue)),
                 asyncio.create_task(self._consume(ml2_queue))]

        await asyncio.gather(*tasks)

    def run(self) -> None:
        """
        Wrapper function for starting run_async.
        """
        try:
            asyncio.run(self._run_async())
        except Exception as e:
            print(e)
            os.kill(os.getpid(), signal.SIGTERM)


def cli_run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tickers", nargs="*", required=True,
        help="Tickers to run in websocket"
    )
    args = parser.parse_args()

    worker = WebSocketWorker(None, None, args.tickers)
    worker.run()
