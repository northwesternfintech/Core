import multiprocessing
import os
from typing import Optional

from .backtest_manager import BacktestManager
from .web_socket_manager import WebSocketManager
from .utils import find_open_port

import zmq
import subprocess
import signal

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

        self._address = "127.0.0.1"
        self._pub_sub_port = 50001

        self._max_cores = multiprocessing.cpu_count()
        self._cur_worker_count = 0

        self._web_socket_manager = WebSocketManager(self)  # TODO
        self._backtest_manager = BacktestManager(self)

        # Start interchange
        interchange_cmd = (
            "interchange "

        )

        interchange_process = subprocess.Popen(interchange_cmd.split(), shell=False,
                                               start_new_session=True)
        self._interchange_pid = interchange_process.pid

    def shutdown(self):
        """Deallocates all necessary resources"""
        for pid in self.web_sockets._running_pids.copy():
            self.web_sockets.stop(pid)

        os.kill(self._interchange_pid, signal.SIGTERM)

    @property
    def web_sockets(self) -> WebSocketManager:
        """Provides access to web sockets"""
        return self._web_socket_manager

    @property
    def backtest(self) -> BacktestManager:
        """Provides access to backtest"""
        return self._backtest_manager


def main():
    import time
    print(os.getpid())
    w = Manager()
    time.sleep(2)
    p = w.web_sockets.start(["BTC-USDT", "ETH-USDT"])
    print(p)
    print(w.web_sockets.status(p))
    time.sleep(5)
    w.shutdown()
    print(w.web_sockets.status(p))
    time.sleep(1)
    w.web_sockets.clear_status()
    print(w.web_sockets._pid_status)
