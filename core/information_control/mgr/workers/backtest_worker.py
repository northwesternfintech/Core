import argparse
import asyncio
import functools
import json
import signal
from typing import List, Optional

import zmq


class BacktestWorker:
    """Worker class for running backtests."""
    def __init__(self):
        """Creates a worker to run a backtest.

        Parameters
        ----------
        """

    def _handle_sigterm(self, signame):
        """Cancels tasks on SIGTERM.

        Parameters
        ----------
        signame : str
            Name of signal (ignored).
        """
        for task in self._produce_tasks:
            task.cancel()

        for task in self._consume_tasks:
            task.cancel()

    async def _live_produce(self):
        """Pulls data from interchange and places it on
        live queue for backtesting.
        """
        for ticker in self._tickers:
            self._socket.setsockopt_string(zmq.SUBSCRIBE, ticker)

        while True:
            data = await self._socket.recv()
            await self._live_queue.put(data)

    async def _live_consume(self, **kwargs):
        """Pulls data off of live queue and calls backtester.
        
        Parameters
        ----------
        kwargs
            Keyword arguments for backtester
        """
        while True:
            data = await self._live_queue.get()
            print(data)  # Will eventually make call to backtester

    async def _run_live(self, **kwargs):
        """Asynchronously pulls data from interchange
        and feeds to backtester.
        
        Parameters
        ----------
        kwargs
            Keyword arguments to backtester.
        """
        self._kill_event = asyncio.Event()
        loop = asyncio.get_event_loop()

        loop.add_signal_handler(signal.SIGTERM,
                                functools.partial(self._handle_sigterm, signal.SIGTERM))

        self._produce_tasks = [asyncio.create_task(self._live_produce())]
        self._consume_tasks = [asyncio.create_task(self._live_consume(**kwargs))]

        await asyncio.gather(*self._consume_tasks)

    def _run_historical(self, **kwargs):
        print(**kwargs)
        pass

    def run(self, mode: str, **kwargs) -> None:
        """Wrapper function for running worker.

        Parameters
        ----------
        mode : str
            'historical' to test on historical data, 'live' to
            test on live data, by default 'historical.
        **kwargs
            Keyword arguments for backtesting.
        """
        if mode == 'live':
            required_args = ['address', 'port', 'tickers']

            for arg in required_args:
                if arg not in kwargs:
                    raise ValueError(f"Missing argument {arg}")

            self._address = kwargs['address']
            self._port = kwargs['port']
            self._tickers = kwargs['tickers']
            self._context = zmq.asyncio.Context()
            self._socket = self._context.socket(zmq.SUB)
            self._socket.connect(f"tcp://{self._address}:{self._port}")
            self._live_queue = asyncio.Queue()
            asyncio.run(self._run_live(**kwargs))
        elif mode == 'historical':
            self._run_historical(**kwargs)
        else:
            raise ValueError(f"Invalid mode '{mode}'")


def cli_run():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode", required=True,
        help="'historical' or 'live''"
    )
    args = parser.parse_args()
    kwargs = dict((k, v) for k, v in vars(args).items())

    worker = BacktestWorker()
    worker.run(args.mode, **kwargs)
