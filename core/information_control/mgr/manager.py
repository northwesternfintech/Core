import multiprocessing
import os
import signal
import subprocess
import time
from typing import Optional

from .backtest_manager import BacktestManager
from .web_socket_manager import WebSocketManager

__all__ = ('Manager',)


class Manager:
    """Manages the startup/operation/teardown of other core services
    and facilitates the flow of data.
    """
    def __init__(self,
                 path: Optional[str] = None,
                 address: str = '127.0.0.1',
                 pub_port: Optional[int] = 50001,
                 sub_port: Optional[int] = 50002,):
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

        self._address = address
        self._pub_port = pub_port
        self._sub_port = sub_port

        self._max_cores = multiprocessing.cpu_count() - 1  # -1 due to interchange
        self._cur_worker_count = 0

        self._web_socket_manager = WebSocketManager(self)  # TODO
        self._backtest_manager = BacktestManager(self)

        # Start interchange
        interchange_cmd = (
            "interchange "
            f"--address {self._address} "
            f"--pub_sub_ports {self._pub_port},{self._sub_port} "
        )

        interchange_process = subprocess.Popen(interchange_cmd.split(), shell=False,
                                               start_new_session=True)
        self._interchange_pid = interchange_process.pid

    def shutdown(self):
        """Deallocates all necessary resources. No manager operations 
        should be done after calling this function."""
        for pid in self.web_sockets._running_pids.copy():
            self.web_sockets.stop(pid)

        time.sleep(1)  # Delay to allow termination messsages to send
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
