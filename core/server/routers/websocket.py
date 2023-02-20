import logging
import uuid
from typing import List

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from ..utils import send_zmq_req
from .. import protocol
import json

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/websocket"
)


@router.post('/start')
async def start_websockets(info: Request):
    """Starts web socket. Validating ticker names is the
    responsibility of the Manager.

    Request Parameters
    ------------------
    ticker_names : List[str]
        List of names of tickers to start

    Returns
    -------
    200, uuid
        Returns worker uuid if successfully starts web socket
    500, details
        Returns error details if encounters server error
    """
    req_info = await info.json()
    message = ["websocket", "start", json.dumps(req_info)]
    address = "tcp://localhost:5557"
    res = await send_zmq_req(message, address)

    if len(res) != 2:
        raise JSONResponse(status_code=500, detail=f"Bad server response: {res}")

    print(res)
    status = res[0]
    status_code = 200 if status == protocol.ACK else 500

    if status_code == 500:
        details = res[1].decode()
        raise HTTPException(
            status_code=500,
            detail=details
        )

    worker_uuid = res[1].decode()
    print(worker_uuid)
    return worker_uuid


@router.post('/stop/{worker_uuid}')
async def stop_websockets(worker_uuid):
    """Stops web sockets. Validating web socket uuids is the
    responsibility of the Manager.

    Request Parameters
    ------------------
    worker_uuids : List[str]
        uuid of web sockets to stop

    Returns
    -------
    200
        If successfully stops web sockets
    400
        If malformed inputs
    404
        If uuid name can't be found
    500
        If fails to stop websocket
    """
    message = ["websocket", "stop", json.dumps({"uuid": worker_uuid})]
    address = "tcp://localhost:5557"
    res = await send_zmq_req(message, address)

    if len(res) > 2:
        raise HTTPException(status_code=500, detail=f"Bad server response: {res}")

    status = res[0]

    if status == protocol.ACK:
        return ''
    else:
        status_code = 500
        details = res[1].decode()
        return HTTPException(
            status_code=status_code,
            detail=details
        )


@router.get('/status/{worker_uuid}')
async def websockets_status(worker_uuid: str):
    """Returns status of uuid.

    Request Parameters
    ------------------
    worker_uuid : str
        uuids of web socket to get status of
    Returns
    -------
    str, 200
        If successfully retrieves web socket status
    404
        If failed to find active uuid
    500
        Manager error
    """
    message = ["websocket", "status", json.dumps({"uuid": worker_uuid})]
    address = "tcp://localhost:5557"
    res = await send_zmq_req(message, address)

    if len(res) != 2:
        raise HTTPException(status_code=500, content=f"Bad server response: {res}")

    status = res[0]
    status_code = 200 if status == protocol.ACK else 500

    if status_code == 500:
        details = res[1].decode()
        raise HTTPException(
            status_code=500,
            detail=details
        )

    details = json.loads(res[1].decode())

    return JSONResponse(
        status_code=status_code,
        content=details
    )

