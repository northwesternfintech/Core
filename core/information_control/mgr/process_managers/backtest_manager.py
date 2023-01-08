import os
import signal
import subprocess
from typing import Dict, List, Set, Tuple, Union
import asyncio
import uuid

from ..workers.status import WorkerStatus
from ..workers.backtest_worker import BacktestWorker
from .process_manager import ProcessManager
import logging

logger = logging.getLogger(__name__)


class BacktestManager(ProcessManager):
    """Manages the startup/status/shutdown of backtests."""
    def __init__(self,
                 manager: 'Manager'):
        """Creates a new BacktestManager. Freeing resources is the
        responsibility of the Manager class.

        Parameters
        ----------
        manager : Manager
            Instance of parent Manager
        """
        super().__init__(manager)

    def start(self, mode='historical',
              block=False, **kwargs) -> int:
        """Starts a process to backtest an algorithm.

        Parameters
        ----------
        strategy_name : str
            Name of strategy to backtest. Work in progress
        mode : str, optional
            'historical' to test on historical data, 'live' to
            test on live data, by default 'historical.
        block : bool, optional
            Whether to block the manager during backtesting or
            run asynchronously.
        **kwargs
            Keyword arguments to pass to backtester. The
            backtester is responsible for determining the
            validity of these arguments.

        Returns
        -------
        uuid : int
            uuid of process that was started

        Raises
        ------
        Optional[ValueError]
            Raises ValueError if invalid inputs
        """
        if self._manager._cur_process_count >= self._manager._max_cores:
            raise ValueError("At max process count. Cancel processes to start more")

        backtest_worker = BacktestWorker()
        flag = self._manager._mp_manager.Event()

        future = None
        match mode:
            case 'live':
                future = self._manager._executor.submit(backtest_worker.run_live, 
                                                        kwargs['tickers'],
                                                        self._manager.web_sockets._ticker_queues,
                                                        flag)
            case 'historical':
                pass
            case _:
                raise ValueError(f"Unexpected mode {mode}")

        process_uuid = str(uuid.uuid4())

        # Update status
        self._add_process(process_uuid, flag, future)

        return process_uuid

def main():
    pass
