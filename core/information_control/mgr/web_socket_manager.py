from typing import Dict, List, Optional, Union, Set, Tuple
import multiprocessing
import subprocess
from uuid import uuid4

import os
import signal

from .status import WebSocketStatus
from .coinbase import CoinbaseWebSocket

import asyncio
import psutil


class WebSocketManager:
    """Manages the startup/status/shutdown of web sockets.

    self._manager : Manager
        Instance of parent Manager
    self._running_pids : Set[str]
        Set of PIDs of running processes
    self._running_tickers : Set[str]
        Set of tickers currently being retrieved
    self._pid_tickers : Dict[str, Set[str]]
        Map of PIDs to set of tickers the process is running
    self._pid_status : Dict[str, WebSocketStatus]
        Map of PIDs to process status
    self._async_tasks : Dict[str]
        Map of PIDs to cancellable async routine
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
        self._manager = manager

        self._running_pids: Set[int] = set()
        self._running_tickers: Set[int] = set()

        self._pid_tickers: Dict[int, Set[str]] = {}
        self._pid_status: Dict[int, WebSocketStatus] =  {}
        self._pid_process: Dict[int] = {}

    def start(self, tickers: List[str]) -> str:
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
        pid : str
            PID of process that was started

        Raises
        ------
        Optional[ValueError]
            Raises ValueError if invalid inputs
        """
        # Validate inputs
        if len(set(tickers)) != len(tickers):
            raise ValueError("Duplicate tickers")

        tickers = set(tickers)

        if tickers & self._running_tickers:
            raise ValueError(f"{tickers & self._running_tickers} tickers already running")

        if self._manager._cur_worker_count >= self._manager._max_cores:
            raise ValueError("At max process count. Cancel processes to start more")

        # TODO: Web socket level verification to ensure ticker names are valid tickers

        cmd = (
            f"web-socket-worker "
            f"--tickers {' '.join(tickers)} "
        )

        # Update status
        process = subprocess.Popen(cmd.split(), shell=False, start_new_session=True)
        pid = process.pid

        self._running_pids.add(pid)
        self._running_tickers.update(tickers)
        
        self._pid_tickers[pid] = tickers
        self._pid_status[pid] = WebSocketStatus.WORKING
        self._pid_process[pid] = process

        return pid

    def stop(self, pid: str) -> Optional[ValueError]:
        """Takes a list of web socket names and stops the appropriate 
        web sockets. Stopping web sockets should not affect any other 
        web sockets.

        Returns (not raises) error if given duplicate web sockets, 
        invalid web sockets, or web sockets that are not running.

        Parameters
        ----------
        sockets_to_stop : List[str]
            List of names of web sockets to run

        Returns
        -------
        Optional[ValueError]
            Returns ValueError if invalid inputs
        """
        # Call cancel on web socket task
        if pid not in self._running_pids:
            raise ValueError()

        os.kill(pid, signal.SIGTERM)

        self._running_pids.remove(pid)
        self._running_tickers -= self._pid_tickers[pid]
        self._pid_tickers.pop(pid)
        self._pid_status[pid] = WebSocketStatus.STOPPED
        self._pid_process.pop(pid)


    def status(self, pid: str) -> Union[str, ValueError]:
        """Takes name of web socket and returns the operational status.

        Returns (not raises) error if given invalid web socket name.

        Parameters
        ----------
        socket_name : str
            Name of web socket to get status of

        Returns
        -------
        Union[str, ValueError]
            Returns ValueError if invalid input or returns status
        """
        if pid not in self._pid_status:
            raise ValueError(f"Unknown PID {pid}")

        self._update_status()
        return self._pid_status[pid]

    def clear_status(self):
        """
        Removes all STOPPED or FAILED websockets
        """
        pid_to_clear = []
        for pid, status in self._pid_status.items():
            if status in [WebSocketStatus.STOPPED, WebSocketStatus.FAILED]:
                pid_to_clear.append(pid)

        for pid in pid_to_clear:
            self._pid_status.pop(pid)


    def _update_status(self):
        """
        Checks whether running web sockets are still operational
        """
        failed_pids = []
        for pid in self._running_pids:
            process = self._pid_process[pid]
            print(process.poll())
            if process.poll() and process.poll() < 0:
                failed_pids.append(pid)

        for pid in failed_pids:
            self._running_pids.remove(pid)
            self._running_tickers -= self._pid_tickers[pid]
            self._pid_tickers.pop(pid)
            self._pid_status[pid] = WebSocketStatus.FAILED
            self._pid_process.pop(pid)


def main():
    w = WebSocketManager(Manager())
    p = w.start(["BTC-USDT"])
    print(p)
    import time
    time.sleep(10)
    w.stop(p)