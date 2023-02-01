import logging
import uuid
from typing import Dict, List, Set, Union

from ...workers.web_socket_worker import WebSocketWorker
from .process_manager import ProcessManager
from ... import protocol
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
        self._redis_conn = self._manager._redis_conn
        self._mgr_be = self._manager._mgr_be
        self._worker_fe = self._manager._worker_fe

    async def _consumer_message(self, address, command, params):
        res = False
        match command:
            case "start":
                res = await self._start_worker(address, **params)
            case "stop":
                res = await self._stop_worker(address, **params)
            case "status":
                res = await self._get_status(address, **params)
            case _:
                msg = [address, f"Invalid command {command} for 'websocket'"]
                self._mgr_be.send_multipart(msg)

        if res:
            msg = [address, protocol.ACK]
            await self._mgr_be.send_multipart(msg)

    async def _start_worker(self, address, **params):
        # Check and validate params
        worker_uuid = uuid.uuid4()

        # Generate command to start worker
        num_processes = await self._redis_conn.get("num_processes")

        if num_processes <= 0:
            msg = [address, b"Too many processes"]
            await self._mgr_be.send_multipart(msg)

        await self._redis_conn.decr("num_processes")

        # Start worker using subprocess

        worker_entry = {
            "worker_uuid": worker_uuid,
            "worker_type": "web_socket",
            "exchange": params["exchange"],
            "tickers": params["tickers"],
            "status": "STARTING",
            "status_details": ""
        }

        await self._redis_conn.set(worker_uuid, worker_entry)

        msg = [address, protocol.ACK]
        await self._mgr_be.send_multipart(msg)

    async def _stop_worker(self, client_address, **params):
        entry = await self._fetch_redis_entry(client_address, **params)

        if entry is None:
            return

        worker_address = params["worker_address"]

        if entry["worker_type"] != "web_socket":
            msg = [client_address, f"No web socket with uuid {worker_address}".encode()]
            await self._mgr_be.send_multipart(msg)
            return

        msg = [worker_address, protocol.DIE]
        await self._worker_fe.send_multipart(msg)

        entry["status"] = "STOPPED"
        entry["status_details"] = ""

        await self._redis_conn.set(worker_address, entry)

        msg = [client_address, protocol.ACK]
        await self._mgr_be.send_multipart(msg)

    async def _get_status(self, client_address, **params):
        entry = await self._fetch_redis_entry(client_address, **params)

        if entry is None:
            return

        worker_address = params["worker_address"]

        if entry["worker_type"] != "web_socket":
            msg = [client_address, f"No web socket with uuid {worker_address}".encode()]
            await self._mgr_be.send_multipart(msg)
            return

        msg = [client_address, protocol.ACK, json.dumps(entry).encode()]
        await self._mgr_be.send_multipart(msg)


def main():
    pass
