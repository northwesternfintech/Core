import os
import signal
import subprocess
from typing import Dict, List, Set, Tuple, Union
import logging
import psutil
import time
import asyncio

import concurrent.futures

from ..workers.status import WorkerStatus
from .process_manager import ProcessManager
from ..workers.web_socket_worker import WebSocketWorker

logger = logging.getLogger(__name__)


class WebSocketManager(ProcessManager):
    """Manages the startup/status/shutdown of web sockets.

    self._running_tickers : Set[str]
        Set of tickers currently being retrieved
    self._pid_tickers : Dict[str, Set[str]]
        Map of PIDs to set of tickers the process is running
    self._pid_process : Dict[int, subprocess.Popen]
        Map of PIDs to processes
    """
    def __init__(self,
                 manager: 'Manager'):
        """Creates a new WebSocketManager. Freeing resources is the
        responsibility of the Manager class.

        Parameters
        ----------
        manager : Manager
            Instance of parent Manager
        """
        super().__init__(manager)

        self._running_tickers: Set[str] = set()
        self._ticker_queues: Dict = {}

    def start(self, tickers: List[str]) -> int:
        """Takes a list of ticker names and starts a websocket to retrieve
        ticker information in a separate processs. Currently there will only
        be a single thread running in each process.

        Raises error if given duplicate tickers, invalid tickers, or tickers
        that are already being retrieved.

        Parameters
        ----------
        tickers : List[str]
            List of tickers to retrieve

        Returns
        -------
        pid : int
            PID of process that was started

        Raises
        ------
        Optional[ValueError]
            Raises ValueError if invalid inputs
        """
        # Validate inputs
        if len(set(tickers)) != len(tickers):
            raise ValueError("Duplicate tickers")

        tickers_set = set(tickers)

        if tickers_set & self._running_tickers:
            raise ValueError(f"{tickers_set & self._running_tickers} tickers already running")

        if self._manager._cur_worker_count >= self._manager._max_cores:
            raise ValueError("At max process count. Cancel processes to start more")

        ws_worker = WebSocketWorker(tickers)

        ml1_queues = {}
        ml2_queues = {}

        for ticker in tickers_set:
            ml1_queues[ticker] = self._manager._mp_manager.Queue()
            ml2_queues[ticker] = self._manager._mp_manager.Queue()

        f = self._manager._executor.submit(ws_worker.run, 
                                           ml1_queues,
                                           ml2_queues,
                                           self._manager._mp_manager.Event())

        while True:
            print(ml1_queues["ETH/USDT"].get())

        # TODO: Web socket level verification to ensure ticker names are valid tickers

        # Start worker
        # cmd = (
        #     f"web-socket-worker "
        #     f"--tickers {' '.join(tickers)} "
        # )

        # process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE)
        # self.process = process
        # pid = process.pid

        # # Update status
        # self._add_worker(pid, process)

        # self._running_tickers.update(tickers_set)
        # self._pid_tickers[pid] = tickers_set

        # print(pid)
        # await process.wait()

    def stop(self, pid: int) -> None:
        """Takes a PID of a web socket process and terminates it.

        Returns (not raises) error if given duplicate web sockets,
        invalid web sockets, or web sockets that are not running.

        Parameters
        ----------
        pid : int
            PID of worker to stop

        Raises
        ------
        ValueError
            Raises ValueError if invalid PID or PID is not running
        """
        if pid not in self._running_pids:
            raise ValueError(f"{pid} is invalid or not running")

        os.kill(pid, signal.SIGTERM)
        self._remove_worker(pid)

    def _remove_worker(self, pid: int) -> None:
        super()._remove_worker(pid)
        self._running_tickers -= self._pid_tickers[pid]
        self._pid_tickers.pop(pid)

    def status(self, pid: int) -> Dict[str, Union[List[str], str]]:
        """Takes PID of web socket and returns the operational status.

        Raises error if given invalid PID.

        Parameters
        ----------
        pid : int
            PID of web socket to get status of

        Returns
        -------
        status_dict : Dict[int, Dict[str, Union[List[str], str]]]
            Dictionary containing "ticker" and "status" of PID.

        Raises
        ------
        ValueError
            Raises ValueError if unknown PID
        """
        if pid not in self._pid_status:
            raise ValueError(f"Unknown PID {pid}")

        self._update_status()

        status_dict = {}

        if pid in self._running_pids:
            status_dict['tickers'] = list(self._pid_tickers[pid])

        status_dict['status'] = str(self._pid_status[pid].value)

        return status_dict

    def _update_status(self):
        failed_pids = []
        for pid in self._running_pids:
            process = self._pid_process[pid]
            if process.poll() is not None and process.poll() < 0:
                failed_pids.append(pid)

        for pid in failed_pids:
            self._remove_worker(pid)

    def status_all(self) -> Dict[int, Dict[str, Union[List[str], str]]]:
        """Returns status of all active PIDs.

        Returns
        -------
        pid_statuses : Dict[int, Dict[str, Union[List[str], str]]]
            Dictionary mapping PIDs to dictionary containing
            "ticker" and "status".
        """
        pid_statuses = {}

        for pid in self._pid_status:
            pid_statuses[pid] = self.status(pid)

        return pid_statuses

def main():
    pass
