import os
import signal
import threading
import time
import argparse
import logging
import logging.handlers
import sys
import datetime

from flask import Flask, jsonify, request

from ..manager import Manager

logger = logging.getLogger(__name__)

app = Flask(__name__)

DIR_HOME = os.path.expanduser('~')
DIR_NUFT = os.path.join(DIR_HOME, '.nuft')


@app.route('/status', methods=['GET'])
def get_status():
    """
    Checks whether server is healthy
    """
    return '', 204


@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Shuts down manager and kills server"""
    try:
        manager.shutdown()
    except Exception as e:
        logger.exception("Manager failed to shutdown")
        return f"Manager returned error {e}", 500

    def self_destruct() -> None:
        for i in range(3, -1, -1):
            logger.info(f"Killing server in {i}...")
            time.sleep(1)
        os.kill(os.getpid(), signal.SIGTERM)

    threading.Thread(target=self_destruct).start()

    return '', 200


@app.route('/web_sockets/start', methods=['POST'])
def start_web_sockets():
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
    request_params = request.json
    ticker_names = []

    try:
        ticker_names = request_params["ticker_names"]
    except KeyError:
        return "Missing field 'ticker_names' in json", 400  # TODO: Return custom error

    if not ticker_names:
        return "No ticker names provided", 400

    try:
        uuid = manager.web_sockets.start(ticker_names)

        return str(uuid), 200
    except ValueError:
        return f"Failed to find tickers {ticker_names}", 404
    except Exception as e:
        logger.exception("Manager failed to start web sockets:")
        return str(e), 500


@app.route('/web_sockets/stop', methods=['POST'])
def stop_web_sockets():
    """Stops web sockets. Validating web socket uuids is the
    responsibility of the Manager.

    Request Parameters
    ------------------
    uuid : List[str]
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
    request_params = request.json
    uuids = None

    try:
        uuids = request_params["uuids"]
    except KeyError:
        return "Missing field 'uuids' in json", 400

    if not uuids:
        return "No uuid provided", 400

    for uuid in uuids:
        try:
            manager.web_sockets.stop(int(uuid))
        except ValueError:
            return f"Failed to find uuid {uuid}", 404
        except Exception as e:
            logger.exception(f"Manager failed to stop {uuid}")
            return str(e), 500

    return '', 200


@app.route('/web_sockets/stop_all', methods=['POST'])
def stop_all_web_sockets():
    """Stops all web sockets.

    Returns
    -------
    200
        If successfully stops web sockets
    500
        If fails to stop websocket
    """
    for uuid in manager.web_sockets._running_uuids.copy():
        try:
            manager.web_sockets.stop(int(uuid))
        except ValueError:
            return f"Failed to find uuid {uuid}", 404
        except Exception as e:
            logger.exception(f"Manager failed to stop {uuid}")
            return str(e), 500

    return '', 200


@app.route('/web_sockets/status/<int:uuid>', methods=['GET'])
def web_sockets_status(uuid):
    """Returns status of uuid

    Request Parameters
    ------------------
    uuid : str
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
        return manager.web_sockets.status(uuid), 200
    except ValueError:
        return f"Failed to find uuid {uuid}", 404
    except Exception as e:
        logger.exception(f"Manager failed to retrieve web socket status of {uuid}")
        return str(e), 500


@app.route('/web_sockets/status/all', methods=['GET'])
def web_sockets_status_all():
    """Returns status of all active uuids

    Returns
    -------
    Dict[int, Tuple[List[str], str]], 200
        If successfully retrieves web socket statuses
    500
        Manager error
    """
    try:
        return jsonify(manager.web_sockets.status_all())
    except Exception as e:
        logger.exception("Manager failed to retrieve all web socket statuses")
        return str(e), 500


@app.route('/web_sockets/status/clear', methods=['POST'])
def web_sockets_status_clear():
    """Clears web socket status

    Returns
    -------
    200
        If successfully clears web socket statuses
    500
        Manager error
    """
    try:
        return jsonify(manager.web_sockets.clear_status())
    except Exception as e:
        logger.exception("Manager failed to clear web socket status")
        return str(e), 500


@app.route('/backtest/start', methods=['POST'])
def start_backtest():
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
    request_params = request.json

    if 'mode' not in request_params:
        return "Missing parameter 'mode'", 400
    try:
        mode = request_params.pop('mode')
        uuid = manager.backtest.start(mode, **request_params)
        return str(uuid), 200
    except Exception as e:
        return str(e), 404


@app.route('/backtest/status/<int:uuid>', methods=['GET'])
def backtest_status(uuid):
    """Returns status of uuid

    Request Parameters
    ------------------
    uuid : str
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
        return manager.backtest.status(uuid), 200
    except ValueError:
        return f"Failed to find uuid {uuid}", 404
    except Exception as e:
        logger.exception(f"Manager failed to retrieve web socket status of {uuid}")
        return str(e), 500


@app.route('/backtest/status/all', methods=['GET'])
def backtest_status_all():
    """Returns status of all active uuids

    Returns
    -------
    Dict[int, Tuple[List[str], str]], 200
        If successfully retrieves web socket statuses
    500
        Manager error
    """
    try:
        return jsonify(manager.backtest.status_all())
    except Exception as e:
        logger.exception("Manager failed to retrieve all web socket statuses")
        return str(e), 500


@app.route('/backtest/status/clear', methods=['POST'])
def backtest_status_clear():
    """Clears web socket status

    Returns
    -------
    200
        If successfully clears web socket statuses
    500
        Manager error
    """
    try:
        return jsonify(manager.backtest.clear_status())
    except Exception as e:
        logger.exception("Manager failed to clear web socket status")
        return str(e), 500


@app.route('/backtest/stop', methods=['POST'])
def stop_backtests():
    """Stops backtest. Validating backtest uuids is the
    responsibility of the Manager.

    Request Parameters
    ------------------
    uuid : List[str]
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
    request_params = request.json
    uuids = None

    try:
        uuids = request_params["uuids"]
    except KeyError:
        return "Missing field 'uuid' in json", 400

    if not uuids:
        return "No uuid provided", 400

    for uuid in uuids:
        try:
            manager.backtest.stop(int(uuid))
        except ValueError:
            return f"Failed to find uuid {uuid}", 404
        except Exception as e:
            logger.exception(f"Manager failed to stop {uuid}")
            return str(e), 500

    return '', 200


@app.route('/backtest/stop_all', methods=['POST'])
def stop_all_backtests():
    """Stops all backtests.

    Returns
    -------
    200
        If successfully stops web sockets
    500
        If fails to stop websocket
    """
    for uuid in manager.backtest._running_uuids.copy():
        try:
            manager.web_sockets.stop(int(uuid))
        except ValueError:
            return f"Failed to find uuid {uuid}", 404
        except Exception as e:
            logger.exception(f"Manager failed to stop {uuid}")
            return str(e), 500

    return '', 200


def cli_run():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--server-address", default='127.0.0.1',
        help="Address to start server on"
    )
    parser.add_argument(
        "--server-port", default=5000,
        help="Port to start server on"
    )
    parser.add_argument(
        "--manager-path", default=DIR_NUFT,
        help="Path to nuft folder for manager to use"
    )
    
    args = parser.parse_args()

    log_dir = os.path.join(args.manager_path, "logs")
    server_log_dir = os.path.join(log_dir, 'server')
    manager_log_dir = os.path.join(log_dir, 'manager')

    if not os.path.exists(server_log_dir):
        os.mkdir(server_log_dir)

    if not os.path.exists(manager_log_dir):
        os.mkdir(manager_log_dir)

    now = datetime.datetime.now()
    server_log_path = now.strftime('%Y-%m-%d') + '.log'
    server_log_path = os.path.join(server_log_dir, server_log_path)

    flask_file_handler = logging.FileHandler(filename=server_log_path, mode='a')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    flask_file_handler.setLevel(logging.INFO)
    flask_file_handler.setFormatter(formatter)

    flask_logger = logging.getLogger('werkzeug')
    flask_logger.setLevel(logging.INFO)
    flask_logger.addHandler(flask_file_handler)

    server_logger = logging.getLogger('core.information_control.mgr.server')
    server_logger.setLevel(logging.INFO)
    server_logger.addHandler(flask_file_handler)

    manager_log_path = now.strftime('%Y-%m-%d') + '.log'
    manager_log_path = os.path.join(manager_log_dir, manager_log_path)

    manager_file_handler = logging.FileHandler(filename=manager_log_path, mode='a')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    manager_file_handler.setLevel(logging.INFO)
    manager_file_handler.setFormatter(formatter)

    manager_logger = logging.getLogger('core.information_control.mgr')
    manager_logger.setLevel(logging.DEBUG)
    manager_logger.addHandler(manager_file_handler)

    global manager

    try:
        manager = Manager(
            path=args.manager_path
        )
    except:
        logger.exception("Manager failed to start")
        return

    out = open(os.devnull, 'w')

    sys.stdout = out
    sys.stderr = out

    app.run(
        host=args.server_address,
        port=args.server_port,
        threaded=False,
        debug=False
    )
