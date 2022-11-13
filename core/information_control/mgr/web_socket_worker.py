import argparse
import asyncio
import functools
import json
import signal
from typing import List

import zmq.asyncio

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
        self._context = zmq.asyncio.Context()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.connect(f"tcp://{self._address}:{self._port}")

    def _handle_sigterm(self, signame):
        """Cancels tasks on SIGTERM

        Parameters
        ----------
        signame : str
            Name of signal (ignored).
        """
        for task in self._produce_tasks:
            task.cancel()

        for task in self._consume_tasks:
            task.cancel()

    async def _send_termination(self):
        """Publishes termination message to all subscribers"""
        for ticker in self._tickers:
            message = f"{ticker} TERMINATE".encode('utf-8')
            await self._socket.send(message)

    async def _consume(self, queue):
        """Consumes data from queue and pushes it to a broker.

        Parameters
        ----------
        queue : asyncio.Queue
            Queue to consume from.
        """
        while True:
            data = await queue.get()
            queue.task_done()

            message = f"{data['ticker']} {json.dumps(data)}".encode('utf-8')
            await self._socket.send(message)

    async def _run_async(self):
        """
        Awaits web socket and consumer tasks asynchronously.
        """
        self._kill_event = asyncio.Event()
        loop = asyncio.get_event_loop()

        loop.add_signal_handler(signal.SIGTERM,
                                functools.partial(self._handle_sigterm, signal.SIGTERM))

        ml1_queue = asyncio.Queue()
        ml2_queue = asyncio.Queue()

        cwr = CoinbaseWebSocket(ml1_queue, ml2_queue, self._tickers)

        self._produce_tasks = [asyncio.create_task(cwr._run())]
        self._consume_tasks = [asyncio.create_task(self._consume(ml1_queue)),
                               asyncio.create_task(self._consume(ml2_queue))]

        await asyncio.gather(*self._consume_tasks)

    def run(self) -> None:
        """
        Wrapper function for starting run_async.
        """
        try:
            asyncio.run(self._run_async())
        except:
            asyncio.run(self._send_termination())


def cli_run():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--address", required=True,
        help="Address to push data to"
    )
    parser.add_argument(
        "--port", required=True,
        help="Port of address to push data to"
    )
    parser.add_argument(
        "--tickers", nargs="*", required=True,
        help="Tickers to run in websocket"
    )
    args = parser.parse_args()

    worker = WebSocketWorker(args.address, args.port, args.tickers)
    worker.run()
