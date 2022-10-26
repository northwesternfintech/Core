from typing import Dict, List, Optional, Union

from .status import BacktestStatus


class BacktestManager:
    """Manages the startup/status/shutdown of backtests.
    """
    def __init__(self, queues: Dict, process_pool,
                 status_dict: Dict[str, BacktestStatus]):
        """Creates a new BacktestManager. Freeing resources is the 
        responsibility of the Manager class.

        Parameters
        ----------
        queues : Dict[str, multiprocessing.Queue]
            Dictionary mapping the names of active web sockets to the 
            queues containing their data
        process_pool : concurrent.futures.ProcessPoolExecutor
            Executor to utilize to start websockets
        status_dict : Dict[str, BacktestStatus]
            Dictionary mapping the names of backtests to their status
        """
        self._queues = queues
        self._process_pool = process_pool
        self._status_dict = status_dict

    def start(self, backtests_to_start: List[str]) -> Optional[ValueError]:
        """Takes a list of backtest names and starts the appropriate 
        backtests in separate processes. Each backtest will have its own 
        process.

        Returns (not raises) error if given duplicate web sockets, 
        invalid web sockets, or web sockets that are already running.

        Parameters
        ----------
        backtests : List[str]
            List of names of backtests to run

        Returns
        -------
        Optional[ValueError]
            Returns ValueError if invalid inputs
        """
        # Validate inputs

        # Update status

        # Start processes with helper function
        pass

    def status(self, backtest_name: str) -> Union[str, ValueError]:
        """Takes name of backtest and return the operational status.

        Returns (not raises) error if given invalid web socket name.

        Parameters
        ----------
        socket_name : str
            Name of backtest to get status of

        Returns
        -------
        Union[str, ValueError]
            Returns ValueError if invalid input or returns status
        """
        # Validate web socket name
        return self._status_dict[backtest_name].value

    @staticmethod
    def _run_process(backtest_to_start: str, queues, status_dict) -> None:
        """Function to be run inside of a process. Responsible for 
        offloading data from the queues to the backtests

        # TODO: See if you can add error handeling

        Parameters
        ----------
        backtest_to_start : str
            Names of backtest to start. Callers of this function are 
            responsible for ensuring the validity of this parameter.
        queues : Dict[str, multiprocessing.Queue]
            Dictionary mapping web socket name to the name of queues 
            to place data in.
        status_dict : Dict[str, WebSocketEnum]
            Dictionary mapping web scoket name to web socket status.
        """
        pass
