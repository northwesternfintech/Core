import os

from typing import Optional, Dict
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Queue

from .web_socket_manager import WebSocketManger


class Manager:
    """Manages the startup/operation/teardown of other core services
    and facilitates the flow of data.
    """
    def __init__(self, path: Optional[str] = None):
        """Creates a new Manger and allocates resources for the manager to use
        (process pool, queues, etc.). It is the responsibility of the user to 
        deallocate these resources using the .shutdown() method.

        Parameters
        ----------
        path : Optional[str], optional
            Absolute path to the nuft folder on this machine. If unspecified
            the path ~/.nuft will be used.
        """
        if path is None:
            path = os.path.join(os.environ['HOME'], '.nuft')

        self._path = path

        self._queue_dict: Dict[Queue] = {}
        self._worker_pool: ProcessPoolExecutor = ProcessPoolExecutor()  # TODO
        self._web_socket_manager = None # TODO

    def shutdown(self):
        """Deallocates all necessary resources"""
        if self._worker_pool:
            self._worker_pool.shutdown(wait=False)


def main():
    manager = Manager()
    print(manager._web_socket_manager)
