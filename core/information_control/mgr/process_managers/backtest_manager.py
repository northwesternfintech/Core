import os
import signal
import subprocess
from typing import Dict, List, Set, Tuple, Union
import asyncio

from ..workers.status import WorkerStatus
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

    async def start(self, mode='historical',
              block=False, **kwargs) -> int:
        """Starts a worker to backtest an algorithm.

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
        pid : int
            PID of process that was started

        Raises
        ------
        Optional[ValueError]
            Raises ValueError if invalid inputs
        """
        if self._manager._cur_worker_count >= self._manager._max_cores:
            raise ValueError("At max process count. Cancel processes to start more")

        cmd = [
            f"backtest-worker "
            f"--mode {mode} "
        ]

        for kwarg_name, kwarg_val in kwargs.items():
            cmd.append(f"--{kwarg_name} {kwarg_val} ")

        logger.error(''.join(cmd).split())
        process = await asyncio.create_subprocess_exec(''.join(cmd).split())
        pid = process.pid

        # Update status
        self._add_worker(pid, process)

        if block:
            process.wait()

        return pid


def main():
    pass
