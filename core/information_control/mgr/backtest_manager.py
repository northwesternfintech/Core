import os
import signal
import subprocess
from typing import Dict, List, Set, Tuple

from .status import BacktestStatus


class BacktestManager:
    """Manages the startup/status/shutdown of backtests.

    self._manager : Manager
        Instance of parent Manager
    self._running_pids : Set[str]
        Set of PIDs of running processes
    self._pid_status : Dict[str, WebSocketStatus]
        Map of PIDs to process status
    self._pid_process : Dict[int, subprocess.Popen]
        Map of PIDs to processes
    """
    def __init__(self,
                 manager: 'Manager'):
        """Creates a new BacktestManager. Freeing resources is the
        responsibility of the Manager class.

        Parameters
        ----------
        manager : Manager
            Instance of parent Manager
        """
        self._manager = manager

        self._running_pids: Set[int] = set()

        self._pid_status: Dict[int, WebSocketStatus] = {}
        self._pid_process: Dict[int, subprocess.Popen] = {}

    def start(self, backtest_name: str, mode='historical',
              data_path=None,
              block=False) -> int:
        """Work in progress

        Parameters
        ----------
        

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
        
        cmd = (
            f"backtest-worker "
        )

        process = subprocess.Popen(cmd.split(), shell=False,
                                   start_new_session=True)
        pid = process.pid

        # Update status
        self._manager._cur_worker_count += 1
        self._running_pids.add(pid)

        self._pid_status[pid] = BacktestStatus.WORKING
        self._pid_process[pid] = process

        return pid

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

        self._manager._cur_worker_count -= 1
        self._running_pids.remove(pid)
        self._running_tickers -= self._pid_tickers[pid]
        self._pid_tickers.pop(pid)
        self._pid_status[pid] = WebSocketStatus.STOPPED
        self._pid_process.pop(pid)

    def status(self, pid: int) -> str:
        """Takes PID of web socket and returns the operational status.

        Raises error if given invalid PID.

        Parameters
        ----------
        pid : int
            PID of web socket to get status of

        Returns
        -------
        str
            Returns PID status

        Raises
        ------
        ValueError
            Raises ValueError if unknown PID
        """
        if pid not in self._pid_status:
            raise ValueError(f"Unknown PID {pid}")

        self._update_status()
        return str(self._pid_status[pid])

    def status_all(self) -> Dict[int, Tuple[List[str], str]]:
        """Returns status of all active PIDs.

        Returns
        -------
        pid_statuses : Dict[int, Tuple[List[str], str]]
            Dictionary mapping PIDs to tickers running and 
            web socket status.
        """
        pid_statuses = {}

        for pid in self._pid_status:
            pid_tickers = []
            if pid in self._running_pids:
                pid_tickers = list(self._pid_tickers[pid])

            pid_statuses[pid] = (pid_tickers, self.status(pid))

        return pid_statuses

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
            if process.poll() and process.poll() < 0:
                failed_pids.append(pid)

        for pid in failed_pids:
            self._manager._cur_worker_count -= 1
            self._running_pids.remove(pid)
            self._running_tickers -= self._pid_tickers[pid]
            self._pid_tickers.pop(pid)
            self._pid_status[pid] = WebSocketStatus.FAILED
            self._pid_process.pop(pid)


def main():
    pass
