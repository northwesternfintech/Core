import argparse
import asyncio
import functools
import json
import signal
from typing import List, Optional
import time

import sys


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
            print("Cancelling")
            task.cancel()

        for task in self._consume_tasks:
            print("Cancelling")
            task.cancel()

    async def _live_produce(self):
        """Pulls data from interchange and places it on
        live queue for backtesting.
        """
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        while True:
            data = await reader.readline()
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
            self._live_queue.task_done()
            t = time.time()
            d = json.loads()
            
            if "time" in d:
                print(t - int(d['time']))
            print(data)  # Will eventually make call to backtester

    async def _run_live(self, **kwargs):
        """Asynchronously pulls data from interchange
        and feeds to backtester.
        
        Parameters
        ----------
        kwargs
            Keyword arguments to backtester.
        """
        self._live_queue = asyncio.Queue()
        self._kill_event = asyncio.Event()
        loop = asyncio.get_event_loop()

        loop.add_signal_handler(signal.SIGTERM,
                                functools.partial(self._handle_sigterm, signal.SIGTERM))

        self._produce_tasks = [asyncio.create_task(self._live_produce())]
        self._consume_tasks = [asyncio.create_task(self._live_consume(**kwargs))]

        await asyncio.gather(*self._produce_tasks)
        await self._live_queue.join()

        for c in self._consume_tasks:
            c.cancel()

    def _run_historical(self, **kwargs):
        print(kwargs)
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

            self._address = kwargs['address'][0]
            self._port = kwargs['port'][0]
            self._tickers = kwargs['tickers']
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
    args, unknown = parser.parse_known_args()
    print("HERE")
    kwargs = {}
    
    while unknown:
        raw_arg_name = unknown.pop(0)

        arg_name = raw_arg_name.strip('--')
        kwargs[arg_name] = []

        while unknown and not unknown[0].startswith('--'):
            arg = unknown.pop(0)
            kwargs[arg_name].append(arg)
    print(args, kwargs)
    worker = BacktestWorker()
    worker.run(args.mode, **kwargs)
