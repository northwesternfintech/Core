import os
import signal
import subprocess
from typing import Dict, List, Set, Tuple, Union
import logging
import multiprocessing
import concurrent.futures

from ..workers.status import WorkerStatus
from abc import ABC

logger = logging.getLogger(__name__)


class ProcessManager(ABC):
    """Base class for process managers.

    self._manager : Manager
        Instance of main Manager
    self._running_uuids : Set[str]
        Set of uuids of running processes
    self._uuid_status : Dict[str, WebSocketStatus]
        Map of uuids to process status
    self._uuid_process : Dict[str, multiprocessing.Event]
        Map of uuids to events used to cancel processes
    self._uuid_future : Dict[str, concurrent.futures.Future]
        Map of uuids to futures of running process
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

        self._running_uuids: Set[str] = set()

        self._uuid_status: Dict[str, WorkerStatus] = {}
        self._uuid_flag: Dict[str, subprocess.Popen] = {}
        self._uuid_future: Dict[str, concurrent.futures.Future] = {}

    async def start(self) -> int:
        raise NotImplementedError

    def _add_process(self, uuid: str, flag: multiprocessing.Event, 
                    future: concurrent.futures.Future) -> None:
        """Tracks new process in class variables.

        Parameters
        ----------
        uuid : str
            uuid of new process to track.
        process : multiprocessing.Event
            Event to set to cancel task
        """
        self._manager._cur_process_count += 1
        logger.error(f"Added uuid {uuid}")
        self._running_uuids.add(uuid)

        self._uuid_status[uuid] = WorkerStatus.WORKING
        self._uuid_flag[uuid] = flag
        self._uuid_future[uuid] = future

    def stop(self, uuid: str) -> None:
        """Takes a uuid of process and terminates it.

        Parameters
        ----------
        uuid : str
            uuid of process to stop

        Raises
        ------
        ValueError
            Raises ValueError if invalid uuid or uuid is not running
        """
        if uuid not in self._running_uuids:
            raise ValueError(f"{uuid} is invalid or not running")

        flag = self._uuid_flag[uuid]
        flag.set()
        self._remove_process(uuid)

    def _remove_process(self, uuid: int) -> None:
        """Removes process from class variables.

        Parameters
        ----------
        uuid : int
            uuid of new process to remove.

        Raises
        ______
        ValueError
            Raises ValueError if invalid uuid or uuid is not running
        """
        self._manager._cur_process_count -= 1
        self._running_uuids.remove(uuid)
        self._uuid_status[uuid] = WorkerStatus.STOPPED
        self._uuid_flag.pop(uuid)
        self._uuid_future.pop(uuid)

    def status(self, uuid: int) -> Dict[str, Union[List[str], str]]:
        """Takes uuid of process and returns the operational status.

        Parameters
        ----------
        uuid : int
            uuid of web socket to get status of

        Returns
        -------
        status_dict : Dict[int, Dict[str, Union[List[str], str]]]
            Dictionary containing "status" of uuid.

        Raises
        ------
        ValueError
            Raises ValueError if unknown uuid
        """
        if uuid not in self._uuid_status:
            raise ValueError(f"Unknown uuid {uuid}")

        self._update_status()

        status_dict = {}
        status_dict['status'] = str(self._uuid_status[uuid].value)

        return status_dict

    def status_all(self) -> Dict[int, Dict[str, Union[List[str], str]]]:
        """Returns status of all active uuids.

        Returns
        -------
        uuid_statuses : Dict[int, Dict[str, Union[List[str], str]]]
            Dictionary mapping uuids to dictionary containing values
            returned by .status.
        """
        uuid_statuses = {}

        for uuid in self._uuid_status:
            uuid_statuses[uuid] = self.status(uuid)

        return uuid_statuses

    def clear_status(self):
        """Removes all STOPPED or FAILED websockets"""
        uuid_to_clear = []
        for uuid, status in self._uuid_status.items():
            if status in [WorkerStatus.STOPPED, WorkerStatus.FAILED]:
                uuid_to_clear.append(uuid)

        for uuid in uuid_to_clear:
            self._uuid_status.pop(uuid)

    def _update_status(self):
        """
        Checks whether running processes are still operational
        """
        failed_uuids = []
        for uuid in self._running_uuids:
            future = self._uuid_future[uuid]
            if future.done() and future.exception():
                failed_uuids.append(uuid)

        for uuid in failed_uuids:
            self._remove_process(uuid)

    def shutdown(self):
        """Stops all running web sockets. Object should not
        be used again after calling this method"""
        for uuid in self._running_uuids.copy():
            logger.error(f"Stopping {uuid}")
            self.stop(uuid)
