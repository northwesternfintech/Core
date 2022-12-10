import os
import signal
import subprocess
from typing import Dict, List, Set, Tuple, Union

from ..workers.status import WorkerStatus
from abc import ABC


class ProcessManager(ABC):
    """Base class for process managers.

    self._manager : Manager
        Instance of main Manager
    self._running_pids : Set[str]
        Set of PIDs of running processes
    self._pid_status : Dict[str, WebSocketStatus]
        Map of PIDs to process status
    self._pid_process : Dict[int, subprocess.Popen]
        Map of PIDs to processes
    """
    def __init__(self,
                 manager: 'Manager'):
        """Creates a new process manager. Freeing resources is the
        responsibility of the Manager class.

        Parameters
        ----------
        manager : Manager
            Instance of parent Manager
        """
        self._manager = manager

        self._running_pids: Set[int] = set()

        self._pid_status: Dict[int, WorkerStatus] = {}
        self._pid_process: Dict[int, subprocess.Popen] = {}

    def start(self) -> int:
        """Starts a worker to backtest an algorithm. Work
        in progress

        Returns
        -------
        pid : int
            PID of process that was started
        """
        raise NotImplementedError

    def _add_worker(self, pid: int, process: subprocess.Popen) -> None:
        """Tracks new process in class variables.

        Parameters
        ----------
        pid : int
            PID of new process to track.
        process : subprocess.Popen
            Process object to track.
        """
        self._manager._cur_worker_count += 1
        self._running_pids.add(pid)

        self._pid_status[pid] = WorkerStatus.WORKING
        self._pid_process[pid] = process

    def stop(self, pid: int) -> None:
        """Takes a PID of a backtest worker and terminates it.

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

    def _remove_worker(self, pid: int) -> None:
        """Removes worker from class variables.

        Parameters
        ----------
        pid : int
            PID of new process to remove.

        Raises
        ______
        ValueError
            Raises ValueError if invalid PID or PID is not running
        """
        self._manager._cur_worker_count -= 1
        self._running_pids.remove(pid)
        self._pid_status[pid] = WorkerStatus.STOPPED
        self._pid_process.pop(pid)

    def status(self, pid: int) -> Dict[str, Union[List[str], str]]:
        """Takes PID of process and returns the operational status.

        Parameters
        ----------
        pid : int
            PID of web socket to get status of

        Returns
        -------
        status_dict : Dict[int, Dict[str, Union[List[str], str]]]
            Dictionary containing "status" of PID.

        Raises
        ------
        ValueError
            Raises ValueError if unknown PID
        """
        if pid not in self._pid_status:
            raise ValueError(f"Unknown PID {pid}")

        self._update_status()

        status_dict = {}
        status_dict['status'] = str(self._pid_status[pid].value)

        return status_dict

    def status_all(self) -> Dict[int, Dict[str, Union[List[str], str]]]:
        """Returns status of all active PIDs.

        Returns
        -------
        pid_statuses : Dict[int, Dict[str, Union[List[str], str]]]
            Dictionary mapping PIDs to dictionary containing values
            returned by .status.
        """
        pid_statuses = {}

        for pid in self._pid_status:
            pid_statuses[pid] = self.status(pid)

        return pid_statuses

    def clear_status(self):
        """Removes all STOPPED or FAILED websockets"""
        pid_to_clear = []
        for pid, status in self._pid_status.items():
            if status in [WorkerStatus.STOPPED, WorkerStatus.FAILED]:
                pid_to_clear.append(pid)

        for pid in pid_to_clear:
            self._pid_status.pop(pid)

    def _update_status(self):
        """
        Checks whether running processes are still operational
        """
        failed_pids = []
        for pid in self._running_pids:
            process = self._pid_process[pid]
            if process.poll() is not None and process.poll() < 0:
                failed_pids.append(pid)

        for pid in failed_pids:
            self._remove_worker(pid)

    def shutdown(self):
        """Stops all running web sockets. Object should not
        be used again after calling this method"""
        for pid in self._running_pids.copy():
            self.stop(pid)
