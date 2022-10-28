from typing import Dict, List, Optional, Union

from .status import WebSocketStatus


class WebSocketManager:
    """Manages the startup/status/shutdown of web sockets.
    """
    def __init__(self,
                 manager: 'Manager',
                 sockets_per_thread=2):
        """Creates a new WebSocketManager. Freeing resources is the 
        responsibility of the Manager class.

        Parameters
        ----------
        manager : Manager
            Instance of parent Manager
        status_dict : Dict[str, WebSocketStatus]
            Dictionary mapping the names of web sockets to their status
        """
        self._manager = manager
        self._sockets_per_thread = sockets_per_thread
        self._async_tasks: Dict[str] = {}  # Maps web socket name to async task

    def start(self, sockets_to_start: List[str]) -> Optional[ValueError]:
        """Takes a list of web socket names and starts the appropriate 
        web sockets in separate processes. There will be 
        self.sockets_per_thread sockets running in a single thread, and 
        one thread running in each process.

        Returns (not raises) error if given duplicate web sockets, 
        invalid web sockets, or web sockets that are already running.

        Parameters
        ----------
        sockets_to_start : List[str]
            List of names of web sockets to run

        Returns
        -------
        Optional[ValueError]
            Returns ValueError if invalid inputs
        """
        # Validate inputs

        # Update status

        # Split up sockets into correct sized batches

        # Start processes with helper function
        pass

    def stop(self, sockets_to_stop: List[str]) -> Optional[ValueError]:
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
        pass

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

    @staticmethod
    def _run_process(sockets_to_start: List[str], queues, status_dict,
                     async_tasks) -> None:
        """Function to be run inside of a process. Responsible for 
        starting async tasks, updating async_tasks, updating status_dict.

        # TODO: See if you can add error handeling

        Parameters
        ----------
        sockets_to_start : List[str]
            Names of sockets to start. Callers of this function are 
            responsible for ensuring the validity of this parameter.
        queues : Dict[str, multiprocessing.Queue]
            Dictionary mapping web socket name to the name of queues 
            to place data in.
        status_dict : Dict[str, WebSocketEnum]
            Dictionary mapping web scoket name to web socket status.
        async_tasks : Dict[str, asyncio.Tasks]
            Dictionary mapping web socket name to Tasks.
        """
        # You may need more helper functions to do this
        # Some helpful stuff:
        # https://docs.python.org/3/library/asyncio-task.html
        # create_task, as_completed
        pass
