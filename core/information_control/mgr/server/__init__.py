import os
import signal
import threading
import time
import argparse
import logging
import sys

from flask import Flask, jsonify, request

from ..manager import Manager

app = Flask(__name__)


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
        return f"Manager returned error {e}", 500

    def self_destruct() -> None:
        time.sleep(5)
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
        pid = manager.web_sockets.start(ticker_names)

        return str(pid), 200
    except ValueError as _:
        return f"Failed to find tickers {ticker_names}", 404
    except Exception as e:
        return f"Manager returned error {e}", 500


@app.route('/web_sockets/stop', methods=['POST'])
def stop_web_sockets():
    """Stops web socket. Validating web socket PIDs is the
    responsibility of the Manager.

    Request Parameters
    ------------------
    pid : List[str]
        Pid of web socket to stop

    Returns
    -------
    200
        If successfully stops web sockets
    400
        If malformed inputs
    404
        If PID name can't be found
    """
    request_params = request.json
    pids = None

    try:
        pids = request_params["pid"]
    except KeyError:
        return "Missing field 'pid' in json", 400

    if not pids:
        return "No PID provided", 400

    try:
        for pid in pids:
            try:
                manager.web_sockets.stop(int(pid))
            except ValueError as _:
                return f"Failed to find PID {pid}", 404
        return '', 200
    except Exception as e:
        return f"Manager returned error {e}", 500


@app.route('/web_sockets/status/<int:pid>', methods=['GET'])
def web_sockets_status(pid):
    """Returns status of PID

    Request Parameters
    ------------------
    pid : str
        PIDs of web socket to get status of

    Returns
    -------
    str, 200
        If successfully retrieves web socket status
    404
        If failed to find active PID
    500
        Manager error
    """    
    try:
        return manager.web_sockets.status(pid), 200
    except ValueError as _:
        return f"Failed to find PID {pid}", 404
    except Exception as e:
        return f"Manager returned error {e}", 500

@app.route('/web_sockets/status/all', methods=['GET'])
def web_sockets_status_all():
    """Returns status of all active PIDs

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
        return f"Manager returned error {e}", 500

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
        return f"Manager returned error {e}", 500


@app.route('/backtest/start', methods=['POST'])
def start_backtest():
    """Starts backtests. Validating backtest names is the
    responsibility of the Manager.

    Request Parameters
    ------------------
    backtest_names : List[str]
        List of names of backtests to start

    Returns
    -------
    200
        If successfully starts backtests
    400
        If malformed inputs
    404
        If backtest name can't be found
    """
    return "not implemented", 404
    request_params = request
    backtest_names = []

    try:
        backtest_names = request["backtest_names"]
    except KeyError:
        return ValueError(), 400 # TODO: Return custom error

    if not backtest_names:
        return ValueError(), 400

    try:
        manager.backtest.start(backtest_names)
    except Exception as e:
        return ValueError(), 404 


@app.route('/backtest/status/<string:backtest_name>', methods=['GET'])
def backtest_status(web_socket_name):
    """Returns status of backtest

    Request Parameters
    ------------------
    backtest_name : str
        Name of backtest to get status of

    Returns
    -------
    """    
    return "not implemented", 404
    try:
        return jsonify(manager.backtest.status(web_socket_name))
    except Exception as e:
        return ValueError(), 500


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
        "--manager-path",
        help="Path to nuft folder for manager to use"
    )
    parser.add_argument(
        "--interchange-address", default='127.0.0.1',
        help="Address to start interchange on"
    )
    parser.add_argument(
        "--interchange-pub-port", default=50001,
        help="Pulish port for interchange"
    )
    parser.add_argument(
        "--interchange-sub-port", default=50002,
        help="Subscription port for interchange"
    )
    args = parser.parse_args()

    global manager
    manager = Manager(
        path=args.manager_path,
        address=args.interchange_address,
        pub_port=args.interchange_pub_port,
        sub_port=args.interchange_sub_port
    )

    out = open(os.devnull, 'w')

    sys.stdout = out
    sys.stderr = out

    app.run(
        host=args.server_address,
        port=args.server_port,
        threaded=False,
        debug=False
    )
