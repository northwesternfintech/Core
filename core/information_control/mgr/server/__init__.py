from flask import Flask, jsonify, request

from ..mgr.manager import Manager

app = Flask(__name__)

manager: Manager  = None

@app.route('/status', methods=['GET'])
def get_status():
    """
    Checks whether server is healthy
    """
    return '', 204

@app.route('/web_sockets/list', methods=['GET'])
def list_web_sockets():
    """
    Returns a list of web socket names
    """
    web_socket_names = []
    # TODO: Get web socket names
    return jsonify(web_socket_names)


@app.route('/web_sockets/start', methods=['POST'])
def start_web_sockets():
    """Starts web sockets. Validating web socket names is the
    responsibility of the Manager.

    Request Parameters
    ------------------
    web_socket_names : List[str]
        List of names of web sockets to start

    Returns
    -------
    200
        If successfully starts web sockets
    400
        If malformed inputs
    404
        If web socket name can't be found
    """
    request_params = request
    web_socket_names = []

    try:
        web_socket_names = request["web_socket_names"]
    except KeyError:
        return ValueError(), 400 # TODO: Return custom error

    if not web_socket_names:
        return ValueError(), 400

    try:
        manager.web_sockets.start(web_socket_names)
    except Exception as e:
        return ValueError(), 404 


@app.route('/web_sockets/stop', methods=['POST'])
def stop_web_sockets():
    """Stops web sockets. Validating web socket names is the
    responsibility of the Manager.

    Request Parameters
    ------------------
    web_socket_names : List[str]
        List of names of web sockets to stop

    Returns
    -------
    200
        If successfully stops web sockets
    400
        If malformed inputs
    404
        If web socket name can't be found
    """
    request_params = request
    web_socket_names = []

    try:
        web_socket_names = request["web_socket_names"]
    except KeyError:
        return ValueError(), 400 # TODO: Return custom error

    if not web_socket_names:
        return ValueError(), 400

    try:
        manager.web_sockets.stop(web_socket_names)
    except Exception as e:
        return ValueError(), 404 


@app.route('/web_sockets/status/<string:web_socket_name>', methods=['GET'])
def web_sockets_status(web_socket_name):
    """Returns status of web socket

    Request Parameters
    ------------------
    web_socket_name : str
        Name of web socket to get status of

    Returns
    -------
    """    
    try:
        return jsonify(manager.web_sockets.status(web_socket_name))
    except Exception as e:
        return ValueError(), 500


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
    try:
        return jsonify(manager.backtest.status(web_socket_name))
    except Exception as e:
        return ValueError(), 500


def main():
    print("hello world")
