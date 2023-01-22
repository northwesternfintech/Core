from fastapi import HTTPException, APIRouter, Request
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/backtest'
)

@router.post('/start')
async def start_backtest(info: Request):
    """Starts backtests. Validating backtest parameters is the 
    responsibility of the Manager.

    Request Parameters
    ------------------
    mode : str
        'historical' or 'live'
    kwargs
        Keyword arguments to past to backtester.

    Returns
    -------
    200
        If successfully starts backtesting.
    400
        If malformed inputs.
    """
    req_info = await info.json()

    if 'mode' not in req_info:
        raise HTTPException(status_code=400, detail="Missing parameter 'mode'")

    try:
        mode = req_info['mode']
        worker_uuid = uuid.uuid4()
        # Start worker
        return str(worker_uuid)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get('/status/{worker_uuid}')
def backtest_status(worker_uuid: str):
    """Returns status of uuid.

    Request Parameters
    ------------------
    worker_uuid : str
        uuids of backtest to get status of

    Returns
    -------
    str, 200
        If successfully retrieves backtest status
    404
        If failed to find active uuid
    500
        Manager error
    """    
    try:
        return 
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Failed to find uuid {worker_uuid}")
    except Exception as e:
        logger.exception(f"Manager failed to retrieve web socket status of {worker_uuid}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/status/all')
def backtest_status_all():
    """Returns status of all active uuids.

    Returns
    -------
    Dict[int, Tuple[List[str], str]], 200
        If successfully retrieves web socket statuses
    500
        Manager error
    """
    try:
        # Pull from redis
        return
    except Exception as e:
        logger.exception("Manager failed to retrieve all web socket statuses")
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/status/clear')
def backtest_status_clear():
    """Clears web socket status.

    Returns
    -------
    200
        If successfully clears web socket statuses
    500
        Manager error
    """
    try:
        return
    except Exception as e:
        logger.exception("Manager failed to clear web socket status")
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/stop')
async def stop_backtests(info: Request):
    """Stops backtest. Validating backtest uuids is the
    responsibility of the Manager.

    Request Parameters
    ------------------
    worker_uuids : List[str]
        uuid of backtest to stop

    Returns
    -------
    200
        If successfully stops backtest
    400
        If malformed inputs
    404
        If uuid name can't be found
    """
    req_info = await info.json()

    if 'uuids' not in worker_uuids:
        raise HTTPException(status_code=400, detail="Missing field 'uuid' in json")

    worker_uuids = req_info['uuids']

    if not worker_uuids:
        raise HTTPException(status_code=400, detail="No uuids provided")

    for u in worker_uuids:
        # Check if actually exists
        pass

    for u in worker_uuids:
        try:
            pass
        except ValueError:
            raise HTTPException(status_code=404, detail=f"Failed to find uuid {uuid}")
        except Exception as e:
            logger.exception(f"Manager failed to stop {uuid}")
            raise HTTPException(status_code=500, detail=str(e))


@router.post('/stop_all')
def stop_all_backtests():
    """Stops all backtests.

    Returns
    -------
    200
        If successfully stops web sockets
    500
        If fails to stop websocket
    """
    return