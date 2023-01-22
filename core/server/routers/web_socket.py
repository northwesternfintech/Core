from fastapi import APIRouter, HTTPException, Request
from typing import List
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/web_socket"
)

@router.post('/start')
async def start_web_sockets(info: Request):
    """Starts web socket. Validating ticker names is the
    responsibility of the Manager.

    Request Parameters
    ------------------
    ticker_names : List[str]
        List of names of tickers to start

    Returns
    -------
    200
        If successfully starts web socket
    400
        If malformed inputs
    404
        If web socket name can't be found
    """
    req_info = await info.json()

    if 'ticker_names' not in req_info:
        raise HTTPException(status_code=400, detail="Missing parameter 'ticker_names'")

    ticker_names: List[str] = req_info['ticker_names']

    if not ticker_names:
        raise HTTPException(status_code=400, detail="No ticker names provided")

    try:
        # Generate UUID for process
        # Start subprocess for websocket-worker
        # Confirm that UUID is entered in redis 
        worker_uuid = uuid.uuid4()
        return str(worker_uuid)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Failed to find tickers {ticker_names}")
    except Exception as e:
        logger.exception("Manager failed to start web sockets:")
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/stop')
async def stop_web_sockets(info: Request):
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
    req_info = await info.json()

    if 'uuids' not in req_info:
        raise HTTPException(status_code=400, detail="Missing parameter 'uuids'")

    worker_uuids: List[str] = req_info['uuids']
    
    if not worker_uuids:
        raise HTTPException(status_code=400, detail="No uuid provided")

    for u in worker_uuids:
        # Verify that uuid exists in redis, else return error
        pass

    for u in worker_uuids:
        try:
            # Send stop request to interchange
            # Verify uuid stopped in redis
            pass
        except ValueError:
            raise HTTPException(status_code=404, detail=f"Failed to find uuid {u}")
        except Exception as e:
            logger.exception(f"Manager failed to stop {u}")
            raise HTTPException(status_code=500, detail=str(e))

    return ''


@router.post('/stop_all')
def stop_all_web_sockets():
    """Stops all web sockets.

    Returns
    -------
    200
        If successfully stops web sockets
    500
        If fails to stop websocket
    """
    running_worker_uuids = set()
    # Pull worker uuids from redis

    for u in running_worker_uuids:
        try:
            # Send stop request to interchange
            # Verify uuid stopped in redis
            pass
        except ValueError:
            raise HTTPException(status_code=404, detail=f"Failed to find uuid {u}")
        except Exception as e:
            logger.exception(f"Manager failed to stop {u}")
            raise HTTPException(status_code=500, detail=str(e))

    return ''


@router.get('/status/{worker_uuid}')
def web_sockets_status(worker_uuid: str):
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
    try:
        # Grab status from redis
        return
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Failed to find uuid {worker_uuid}")
    except Exception as e:
        logger.exception(f"Manager failed to retrieve web socket status of {uuid}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/status/all')
def web_sockets_status_all():
    """Returns status of all active uuids.

    Returns
    -------
    Dict[int, Tuple[List[str], str]], 200
        If successfully retrieves web socket statuses
    500
        Manager error
    """
    try:
        # Grab status
        return
    except Exception as e:
        logger.exception("Manager failed to retrieve all web socket statuses")
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/status/clear')
def web_sockets_status_clear():
    """Clears web socket status and returns resulting status.

    Returns
    -------
    200
        If successfully clears web socket statuses
    500
        Manager error
    """
    try:
        # Clear status and return
        return ''
    except Exception as e:
        logger.exception("Manager failed to clear web socket status")
        raise HTTPException(status_code=500, detail=str(e))