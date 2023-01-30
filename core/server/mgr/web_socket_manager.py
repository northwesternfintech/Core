import logging
import uuid
from typing import Dict, List, Set, Union

from ..workers.web_socket_worker import WebSocketWorker
from .process_managers.process_manager import ProcessManager
from .. import protocol
import json

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
        self._manager = manager
        self._broker_socket = self._manager._broker_socket

    async def _consumer_message(self, frames):
        res = self._manager.validate_message(frames, "websocket")

        if not res:
            return

        address, command, params = res
        
        match command:
            case "start":
                await self._start_worker(address, **params)
                break
            case "status":
                await self._get_status(address, **params)
                break
            case "stop":
                await self._stop_worker(address, **params)
                break
            case "update":
                break
            case _:
                msg = [address, f"Invalid command {command} for 'websocket'"]
                self._broker_socket.send_multipart(msg)


def main():
    pass
