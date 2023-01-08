import os
import signal
import subprocess
from typing import Dict, List, Set, Tuple, Union
import logging
import psutil
import time
import asyncio
import uuid

import concurrent.futures

from ..workers.status import WorkerStatus
from .process_manager import ProcessManager
from ..workers.web_socket_worker import WebSocketWorker

logger = logging.getLogger(__name__)


class WebSocketManager(ProcessManager):
    """Manages the startup/status/shutdown of web sockets.

    self._running_tickers : Set[str]
        Set of tickers currently being retrieved
    self._uuid_tickers : Dict[str, Set[str]]
        Map of uuids to set of tickers the process is running
    self._uuid_process : Dict[int, subprocess.Popen]
        Map of uuids to processes
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
        self._uuid_tickers: Dict[str, Set[str]] = {}
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
        uuid : str
            uuid of process that was started

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

        if self._manager._cur_process_count >= self._manager._max_cores:
            raise ValueError("At max process count. Cancel processes to start more")

        ws_worker = WebSocketWorker(tickers)

        ml1_queues = {}
        ml2_queues = {}
        flag = self._manager._mp_manager.Event()

        for ticker in tickers_set:
            ml1_queues[ticker] = self._manager._mp_manager.Queue()
            ml2_queues[ticker] = self._manager._mp_manager.Queue()
            self._ticker_queues[ticker] = (ml1_queues[ticker], ml2_queues[ticker])

        future = self._manager._executor.submit(ws_worker.run, 
                                                ml1_queues,
                                                ml2_queues,
                                                flag)

        process_uuid = str(uuid.uuid4())

        # Update status
        self._add_process(process_uuid, flag, future)

        self._running_tickers.update(tickers_set)
        self._uuid_tickers[process_uuid] = tickers_set

        # while True:
        #     print(ml1_queues["BTC/USDT"].get())

        return process_uuid

    def stop(self, uuid: str) -> None:
        """Takes a uuid of a web socket process and terminates it.

        Returns (not raises) error if given duplicate web sockets,
        invalid web sockets, or web sockets that are not running.

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
        super()._remove_process(uuid)
        self._running_tickers -= self._uuid_tickers[uuid]
        self._uuid_tickers.pop(uuid)

    def status(self, uuid: str) -> Dict[str, Union[List[str], str]]:
        """Takes uuid of web socket and returns the operational status.

        Raises error if given invalid uuid.

        Parameters
        ----------
        uuid : str
            uuid of web socket to get status of

        Returns
        -------
        status_dict : Dict[str, Dict[str, Union[List[str], str]]]
            Dictionary containing "ticker" and "status" of uuid.

        Raises
        ------
        ValueError
            Raises ValueError if unknown uuid
        """
        if uuid not in self._uuid_status:
            raise ValueError(f"Unknown uuid {uuid}")

        self._update_status()

        status_dict = {}

        if uuid in self._running_uuids:
            status_dict['tickers'] = list(self._uuid_tickers[uuid])

        status_dict['status'] = str(self._uuid_status[uuid].value)

        return status_dict

    def _update_status(self):
        failed_uuids = []
        for uuid in self._running_uuids:
            future = self._uuid_future[uuid]
            if future.done() and future.exception():
                failed_uuids.append(uuid)

        for uuid in failed_uuids:
            self._remove_process(uuid)

    def status_all(self) -> Dict[int, Dict[str, Union[List[str], str]]]:
        """Returns status of all active uuids.

        Returns
        -------
        uuid_statuses : Dict[int, Dict[str, Union[List[str], str]]]
            Dictionary mapping uuids to dictionary containing
            "ticker" and "status".
        """
        uuid_statuses = {}

        for uuid in self._uuid_status:
            uuid_statuses[uuid] = self.status(uuid)

        return uuid_statuses

def main():
    pass
