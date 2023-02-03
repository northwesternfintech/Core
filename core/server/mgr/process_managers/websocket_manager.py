import logging
import uuid
from typing import Dict, List, Set, Union, ByteString

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
        self._broker_uuid = self._manager._broker_uuid
        self._redis_conn = self._manager._redis_conn
        self._mgr_be = self._manager._mgr_be
        self._worker_fe = self._manager._worker_fe

    async def _consume_message(self,
                               client_address: ByteString,
                               command: str,
                               params: Dict):
        """Parses command and calls appropriate function. Sends error message to 
        client if invalid command type

        Parameters
        ----------
        client_address : ByteString
            ByteString of address of client
        command : str
            Command that client wants to run
        params : Dict
            Dictionary containing parameters for command
        """
        match command:
            case "start":
                await self._start_worker(client_address, **params)
            case "stop":
                await self._stop_worker(client_address, **params)
            case "status":
                await self._get_status(client_address, **params)
            case _:
                msg_content = [
                    protocol.ERROR,
                    f"Invalid command {command} for 'websocket'".encode()
                ]
                await self._send_client_response(client_address, msg_content)
                return

    async def _start_worker(self, client_address: ByteString, **params):
        """Starts web socket worker and makes a corresponding entry into redis.
        Sends ACK and worker uuid to client if successful, error message if
        unsuccessful

        Parameters
        ----------
        client_address : ByteString
            ByteString of address of client
        **params
            Keyword arguments. Must contain keys "exchange", "tickers"
        """
        # Check and validate params
        worker_uuid = str(uuid.uuid4())

        # Generate command to start worker
        num_workers = await self._redis_conn.get("num_workers")
        num_workers = int(num_workers.decode())

        if num_workers >= self._manager._max_processes:
            msg_content = [
                protocol.ERROR,
                b"Too many active workers. Try again later"
            ]
            await self._send_client_response(client_address, msg_content)
            return

        await self._redis_conn.incr("num_workers")

        # Start worker using subprocess

        worker_entry = {
            "worker_uuid": worker_uuid,
            "worker_type": "websocket",
            "exchange": params["exchange"],
            "tickers": params["tickers"],
            "status": "STARTING",
            "status_details": ""
        }

        await self._redis_conn.set(worker_uuid, json.dumps(worker_entry).encode())

        msg_content = [protocol.ACK, worker_uuid.encode()]
        await self._send_client_response(client_address, msg_content)

    async def _stop_worker(self, client_address: ByteString, **params):
        """Stops web socket worker, messages worker to die, and updates entry in
        redis. Sends ACK to client if successful, error message if
        unsuccessful

        Parameters
        ----------
        client_address : ByteString
            ByteString of address of client
        **params
            Keyword arguments. Must contain keys "uuid". "uuid" must correspond to
            an active web socket worker
        """
        entry = await self._fetch_worker_redis_entry(client_address, **params)

        if entry is None:
            return

        worker_address = params["uuid"]

        if entry["worker_type"] != "websocket":
            msg = [client_address, f"No web socket with uuid {worker_address}".encode()]
            await self._mgr_be.send_multipart(msg)
            return

        # Check if worker is active

        msg_content = [protocol.DIE]
        self._send_worker_message(worker_address, msg_content)

        await self._redis_conn.decr("num_workers")

        entry["status"] = "STOPPED"
        entry["status_details"] = ""

        await self._redis_conn.set(worker_address, json.dumps(entry).encode())

        msg_content = [protocol.ACK]
        await self._send_client_response(client_address, msg_content)

    async def _get_status(self, client_address: ByteString, **params):
        """Retrieves worker status from redis. Sends ACK to client if successful,
        error message if unsuccessful

        Parameters
        ----------
        client_address : ByteString
            ByteString of address of client to send status to
        **params
            Keyword arguments. Must contain keys "uuid". "uuid" must correspond to
            a valid web socket worker
        """
        print("HERE")
        entry = await self._fetch_worker_redis_entry(client_address, **params)
        print(entry)

        if entry is None:
            return

        worker_address = params["uuid"]

        if entry["worker_type"] != "websocket":
            msg_content = [
                protocol.ERROR,
                f"No web socket with uuid {worker_address}".encode()
            ]
            await self._send_client_response(client_address, msg_content)
            return

        msg_content = [protocol.ACK, json.dumps(entry).encode()]
        print(client_address)
        await self._send_client_response(client_address, msg_content)

    async def _shutdown(self):
        return


def main():
    pass
