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

    def run_live(self, tickers, ticker_queues, flag, **kwargs):
        while True:
            if flag and flag.is_set():
                return

            for t in tickers:
                data = ticker_queues[t][0].get()
                
                if not data:
                    return

                print(data)

    def run_historical(self, **kwargs):
        pass
        




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
