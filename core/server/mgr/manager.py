import logging
import multiprocessing
import os
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Optional

from .process_managers.backtest_manager import BacktestManager
from .process_managers.web_socket_manager import WebSocketManager

logger = logging.getLogger(__name__)

__all__ = ('Manager',)


class Manager:
    """Manages the startup/operation/teardown of other core services
    and facilitates the flow of data.
    """
    def __init__(self,
                 path: Optional[str] = None):
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
        self._cur_process_count = 0

        self._executor = ProcessPoolExecutor(self._max_cores)
        self._mp_manager = multiprocessing.Manager()

        self._web_socket_manager = WebSocketManager(self)
        self._backtest_manager = BacktestManager(self)

    def shutdown(self):
        """Deallocates all necessary resources. No manager operations
        should be done after calling this function."""
        self.web_sockets.shutdown()
        logger.error("Shutting down backtest")
        self.backtest.shutdown()

        time.sleep(1)

        self._executor.shutdown()

    @property
    def web_sockets(self) -> WebSocketManager:
        """Provides access to web sockets"""
        return self._web_socket_manager

    @property
    def backtest(self) -> BacktestManager:
        """Provides access to backtest"""
        return self._backtest_manager


def main():
    m = Manager()
    u = m.web_sockets.start(["ETH/USDT", "BTC/USDT"])
    print("HERE")
    v = m.backtest.start(mode='live', tickers=['BTC/USDT', 'ETH/USDT'])

    time.sleep(2)
    # m.backtest.stop(v)
    print(m.backtest.status_all())
    # m.web_sockets.stop(u)
    print(m.web_sockets.status_all())