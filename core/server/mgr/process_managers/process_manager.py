import concurrent.futures
import logging
import multiprocessing
import subprocess
from abc import ABC
from typing import Dict, List, Set, Union, Optional, Tuple, ByteString
from ... import protocol
import json

logger = logging.getLogger(__name__)


class ProcessManager(ABC):
    """Base class for process managers.

    self._manager : Manager
        Instance of main Manager
    self._running_uuids : Set[str]
        Set of uuids of running processes
    self._uuid_status : Dict[str, WebSocketStatus]
        Map of uuids to process status
    self._uuid_process : Dict[str, multiprocessing.Event]
        Map of uuids to events used to cancel processes
    self._uuid_future : Dict[str, concurrent.futures.Future]
        Map of uuids to futures of running process
    """
    def __init__(self, manager):
        self._manager = manager
        self._broker_uuid = self._manager._broker_uuid
        self._redis_conn = self._manager._redis_conn
        self._mgr_be = self._manager._broker_socket
        self._worker_fe = self._manager._worker_socket

    async def _validate_client_message(self, frames: List) -> Optional[Tuple]:
        """Takes raw frames from client response, validates it, and then 
        decodes/parses it and returns the results. A valid client message consists
        of the following:

        1. Client address: the identity of the client's socket as a byte string
        2. Service type: the type of service to interface with as a byte string
        (such as "web_socket" or "backtest")
        3. Command: the command to provide to the service as a byte string (such
        as "start" or "stop")
        4. Params: parameters to pass to the command as a json dumped byte string

        Parameters
        ----------
        frames : List
            Frames forwarded from the client to the manager by the broker

        Returns
        -------
        Optional[Tuple]
            Returns a tuple containing the client address, service type, command
            and params if frames are successfully parsed and validated and returns
            None (and sends error message to client) if validation/parsing fails
        """
        if not frames:
            return

        client_address = frames[0]
        if len(frames) < 4:
            msg_content = [protocol.ERROR, b"Message too short"]
            await self._mgr_be.send_multipart(msg_content)
            return

        service_type = frames[1].decode()
        command = frames[2].decode()
        params = frames[3].decode()

        if params:
            try:
                params = json.loads(params)
            except:
                msg_content = [protocol.ERROR, b"Failed to load params"]
                await self._send_client_response(client_address, msg_content)
                return

        return client_address, service_type, command, params

    async def _fetch_worker_redis_entry(self, client_address: ByteString, **params) -> Optional[Dict]:
        """Retrieves a redis entry for a worker.

        Parameters
        ----------
        client_address : ByteString
            ByteString of the address of the client who initiated the fetch
        **params
            Keyword arguments. Must contain the key "uuid"

        Returns
        -------
        Optional[Dict]
            Returns a dictionary containing the worker entry from redis. Returns 
            None (and sends error message to client) if missing key "uuid" in
            **params or if "uuid" is invalid
        """
        if "uuid" not in params:
            msg_content = [protocol.ERROR, b"Missing parameter 'uuid'"]
            await self._send_client_response(client_address, msg_content)
            return

        worker_address = params["uuid"]
        if not (await self._redis_conn.exists(worker_address)):
            msg_content = [protocol.ERROR, f"Unknown uuid {worker_address}".encode()]
            await self._send_client_response(client_address, msg_content)
            return

        entry = await self._redis_conn.get(worker_address)
        entry = json.loads(entry.decode())
        return entry

    async def _send_client_response(self, client_address: ByteString, message: List):
        """Sends message to client

        Parameters
        ----------
        client_address : ByteString
            ByteString of the address of the client to message
        message : List
            Content of message to send to client
        """
        msg = [self._broker_uuid, client_address] + message
        print(msg)
        await self._mgr_be.send_multipart(msg)
        print("SENT")

    async def _send_worker_message(self, worker_address: ByteString, message: List):
        """Sends message to worker

        Parameters
        ----------
        worker_address : ByteString
            ByteString of the address of the worker to message
        message : List
            Content of message to send to worker
        """
        msg = [self._broker_uuid, worker_address] + message
        print(msg)
        await self._worker_fe.send_multipart(msg)
        print("SENT")
