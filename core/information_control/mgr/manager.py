import os

from typing import Optional, Dict
import multiprocessing

from .web_socket_manager import WebSocketManager
from .backtest_manager import BacktestManager

# TODO: May need to implement a pub sub model for data if multiple backtests using the 
# same stream. If we switch to containers for running backtest maybe we use rabbitmq/kafka

# https://stackoverflow.com/questions/31267366/how-can-i-implement-a-pub-sub-pattern-using-multiprocessing

__all__ = ('Manager',)

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

        self._max_cores = multiprocessing.cpu_count()
        self._cur_worker_count = 0
        self._web_socket_manager = WebSocketManager(self) # TODO
        self._backtest_manager = BacktestManager(self)

    def shutdown(self):
        """Deallocates all necessary resources"""
        for pid in self.web_sockets._running_pids:
            self.web_sockets.stop(pid)

    @property
    def web_sockets(self) -> WebSocketManager:
        """Provides access to web sockets"""
        return self._web_socket_manager

    @property
    def backtest(self) -> BacktestManager:
        """Provides access to backtest"""
        return self._backtest_manager


def main():
    print(os.getpid())
    w = Manager()
    p = w.web_sockets.start(["BTC-USDT"])
    print(p)
    import time
    time.sleep(5)
    print(w.web_sockets.status(p))
    w.web_sockets.stop(p)
    print(w.web_sockets.status(p))
    time.sleep(1)
    w.web_sockets.clear_status()
    print(w.web_sockets._pid_status)
