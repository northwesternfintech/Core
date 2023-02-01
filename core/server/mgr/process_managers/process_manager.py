import concurrent.futures
import logging
import multiprocessing
import subprocess
from abc import ABC
from typing import Dict, List, Set, Union
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
        self._redis_conn = self._manager._redis_conn
        self._broker_socket = self._manager._broker_socket
        self._worker_socket = self._manager._worker_socket

    def _validate_client_message(self, frames):
        if not frames:
            return

        client_address = frames[0]
        if len(frames) < 4:
            msg = [client_address, protocol.ERROR, b"Message too short"]
            self._broker_socket.send_multipart(msg)
            return

        service_type = frames[1].decode()
        command = frames[2].decode()
        params = frames[3].decode()

        if frames[1] != service_type:
            msg = [client_address, protocol.ERROR, b"Invalid service"]
            self._broker_socket.send_multipart(msg)
            return

        if params:
            try:
                params = json.load(params)
            except:
                msg = [client_address, protocol.ERROR, b"Failed to load params"]
                self._broker_socket.sent_multipart(msg)
                return

        return client_address, service_type, command, params

    async def _fetch_redis_entry(self, client_address, **params):
        if "uuid" not in params:
            msg = [client_address, b"Missing param 'uuid'"]
            await self._broker_socket.send_multipart(msg)
            return
        
        worker_address = params["uuid"]
        if not (await self._redis_conn.find(worker_address)):
            msg = [client_address, f"Unknown uuid {worker_address}".encode()]
            await self._broker_socket.send_multipart(msg)
            return

        entry = await self._redis_conn.get(worker_address)
        entry = json.loads(entry)
        return entry
