import argparse
import asyncio
import functools
import json
import signal
from typing import List
import time
import multiprocessing

import zmq.asyncio

from ..coinbase import ccxtws


class WebSocketWorker:
    """Worker class for running a producer/consumer for
    web sockets.
    """
    def __init__(self, tickers: List[str]):
        """Creates a worker to run a web socket.

        Parameters
        ----------
        address : _type_
            _description_
        port : _type_
            _description_
        """
        self._tickers = tickers

    def _handle_sigterm(self, signame):
        """Cancels tasks on SIGTERM

        Parameters
        ----------
        signame : str
            Name of signal (ignored).
        """
        for task in self._produce_tasks:
            task.cancel()

    async def _send_termination(self):
        """Publishes termination message to all subscribers"""
        for ticker in self._tickers:
            message = f"{ticker} TERMINATE".encode('utf-8')
            await self._socket.send(message)

    async def _consume(self, ws_queue, ml_queues):
        """Consumes data from queue and pushes it to a broker.

        Parameters
        ----------
        queue : asyncio.Queue
            Queue to consume from.
        """
        while True:
            data = await ws_queue.get()
            ws_queue.task_done()

            ml_queues[data["ticker"]].put(data)

            # data["time"] = time.time()

            # message = f"{data['ticker']} {json.dumps(data)}".encode('utf-8')
            # print(message)

    async def check_flag(self, flag):
        if not flag:
            return

        while True:
            if flag.is_set():
                self._handle_sigterm("blah")
                return
            
            await asyncio.sleep(0.5)

    async def _run_async(self, ml1_queues, ml2_queues, flag):
        """
        Awaits web socket and consumer tasks asynchronously.
        """
        self._kill_event = asyncio.Event()
        loop = asyncio.get_event_loop()

        loop.add_signal_handler(signal.SIGTERM,
                                functools.partial(self._handle_sigterm, signal.SIGTERM))

        self._ml1_queues = ml1_queues
        self._ml2_queues = ml2_queues
        
        self._ws_ml1_queue = asyncio.Queue()
        self._ws_ml2_queue = asyncio.Queue()

        cwr = ccxtws("", self._ws_ml1_queue, self._ws_ml2_queue, self._tickers)

        self._produce_tasks = [asyncio.create_task(cwr.async_run())]
        # self._flag_task = [asyncio.create_task(self.check_flag(flag))]
        self._consume_tasks = [asyncio.create_task(self._consume(self._ws_ml1_queue, self._ml1_queues)),
                               asyncio.create_task(self._consume(self._ws_ml2_queue, self._ml2_queues))]
        await asyncio.gather(*self._produce_tasks)

    def run(self, ml1_queue, ml2_queue, flag=None) -> None:
        """
        Wrapper function for starting run_async.
        """
        try:
            asyncio.run(self._run_async(ml1_queue, ml2_queue, flag))
        except Exception as e:
            asyncio.run(self._send_termination())


def cli_run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tickers", nargs="*", required=True,
        help="Tickers to run in websocket"
    )
    args = parser.parse_args()

    worker = WebSocketWorker(args.tickers)
    worker.run()
