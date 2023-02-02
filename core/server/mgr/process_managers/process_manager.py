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
        self._broker_uuid = self._manager._broker_uuid
        self._redis_conn = self._manager._redis_conn
        self._mgr_be = self._manager._broker_socket
        self._worker_fe = self._manager._worker_socket

    async def _validate_client_message(self, frames):
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
            except Exception as e:
                msg_content = [protocol.ERROR, b"Failed to load params"]
                await self._send_client_response(client_address, msg_content)
                return

        return client_address, service_type, command, params

    async def _fetch_redis_entry(self, client_address, **params):
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

    async def _send_client_response(self, client_address, message):
        msg = [self._broker_uuid, client_address] + message
        print(msg)
        await self._mgr_be.send_multipart(msg)
        print("SENT")

    async def _send_worker_message(self, worker_address, message):
        msg = [self._broker_uuid, worker_address] + message
        print(msg)
        await self._worker_fe.send_multipart(msg)
        print("SENT")
