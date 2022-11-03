from typing import Dict, List, Optional, Union, Set, Tuple
import multiprocessing
from uuid import uuid4

from .status import WebSocketStatus
from .coinbase import CoinbaseWebSocket

import asyncio


class WebSocketManager:
    """Manages the startup/status/shutdown of web sockets.

    self._manager : Manager
        Instance of parent Manager
    self._running_pids : Set[str]
        Set of UUIDs of running processes
    self._running_tickers : Set[str]
        Set of tickers currently being retrieved
    self._pid_tickers : Dict[str, Set[str]]
        Map of process UUIDs to set of tickers the process is running
    self._pid_status : Dict[str, WebSocketStatus]
        Map of process UUIDs to process status
    self._async_tasks : Dict[str]
        Map of process UUIDs to cancellable async routine
    self._pid_queues : Dict[Tuple[Queue, Queue]]
        Map of process UUIDs to a tuple containing the queues storing
        market level 1 & 2 data
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

        self._running_pids: Set[str] = set()
        self._running_tickers: Set[str] = set()

        self._pid_tickers: Dict[str, Set[str]] = {}
        self._pid_status: Dict[str, WebSocketStatus] =  {}

        self._pid_processes = {}
        self._pid_queues: Dict[Tuple[Queue, Queue]] = {}

    def start(self, tickers: List[str], *args, **kwargs) -> str:
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
            UUID of process that was started

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

        # TODO: Web socket level verification to ensure ticker names are valid tickers

        # Update status
        process = multiprocessing.Process(target=run_process,
                                          args=(tickers, asyncio.Queue(), asyncio.Queue()))
        pid = process.pid
        process.start()
        self._running_pids.add(process.pid)
        self._running_tickers.update(tickers)
        
        self._pid_tickers[pid] = tickers
        self._pid_status[pid] = WebSocketStatus.WORKING

        # self._pid_queues[pid] = (asyncio.Queue(), asyncio.Queue())
        self._pid_processes[process.pid] = process

        # Start processes with helper function
        return process.pid

    def stop(self, pid) -> Optional[ValueError]:
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
        self._pid_processes[pid].terminate()
        self._pid_processes[pid].join(wait=1)

    def status(self, socket_name: str) -> Union[str, ValueError]:
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
        # Validate web socket name
        return self._manager._status_dict[socket_name].value


def main():
    w = WebSocketManager(None)
    w.start(['BTC-USDT', 'ETH-USDT'])