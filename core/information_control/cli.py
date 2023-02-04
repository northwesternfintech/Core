import click
from click import ClickException
import configparser
import os
import subprocess
import requests

from tabulate import tabulate

from .mgr.utils import find_open_ports
from .docker.docker_build_python import repo_to_container

DIR_HOME = os.path.expanduser('~')
DIR_NUFT = os.path.join(DIR_HOME, '.nuft')


class NUFTConfig:
    def __init__(self, config_path: str, nuft_dir: str):
        self.config_path = config_path
        self.nuft_dir = nuft_dir
        self.config = configparser.ConfigParser()

        if os.path.exists(config_path):
            self.config.read(config_path)
        else:
            # TODO: Create default config at location
            pass

        server_port = self.config['server'].get('port')
        server_host = self.config['server'].get('host')

        if not server_host:
            raise ClickException("Missing server host in config")

        if not server_port:
            raise ClickException("Missing server port in config")

        self.server_address = f"http://{server_host}:{server_port}"


@click.group('nuft')
@click.option(
    '-d',
    '--nuft-dir',
    default=DIR_NUFT,
    help='path to directory to store nuft data'
)
@click.option(
    '-c',
    '--config-path',
    default=os.path.join(DIR_NUFT, 'config.ini'),
    help='path to nuft configuration file'
)
@click.pass_context
def app(ctx, nuft_dir: str, config_path: str):
    ctx.obj = NUFTConfig(config_path, nuft_dir)




@app.command('start')
@click.pass_context
def start_server(ctx):
    """Starts manager server"""
    nuft_config = ctx.obj

    server_host = nuft_config.config['server']['host']
    server_port = find_open_ports(1)[0]
    nuft_config.config['server']['port'] = str(server_port)

    manager_path = nuft_config.nuft_dir

    cmd = (
           "manager_server "
           f"--server-address {server_host} "
           f"--server-port {server_port} "
           f"--manager-path {manager_path} "
    )

    try:
        subprocess.Popen(cmd.split(), 
                         shell=False,
                         start_new_session=True)
    except Exception as e:
        raise ClickException(f"Failed to start server: {e}")

    with open(nuft_config.config_path, 'w') as f:
        nuft_config.config.write(f)

@app.group('docker')
def docker_handler():
    pass

@docker_handler.command('generate')
@click.argument('repo')
@click.argument('file')
@click.argument('img')
def docker_generate(repo, file, img):
    result = repo_to_container(repo, file, img)
    click.echo("Done")


@app.command('shutdown')
@click.pass_context
def shutdown_server(ctx):
    """Shutsdown manager server"""
    nuft_config = ctx.obj

    server_host = nuft_config.config['server'].get('host')
    server_port = nuft_config.config['server'].get('port')
    if not (server_host and server_port):
        raise ClickException("Server not running!")

    path = f"{nuft_config.server_address}/shutdown"
    res = requests.post(path)

    if res.status_code != 200:
        raise ClickException(res.text)

    print("Successfully shutdown server")


@app.group('websocket')
def web_socket_handler():
    pass


@web_socket_handler.command('start')
@click.argument(
    'ticker_names',
    nargs=-1,
)
@click.pass_context
def web_socket_start(ctx, ticker_names):
    """Takes multiple ticker names to start

    e.g. `nuft websocket start BTC-USDT ETH USDT`
    """
    ticker_names = list(ticker_names)
    if not ticker_names:
        raise ClickException("Missing ticker names")

    nuft_config = ctx.obj

    path = f"{nuft_config.server_address}/web_sockets/start"
    payload = {
        "ticker_names": ticker_names
    }

    res = requests.post(path, json=payload)

    match res.status_code:
        case 200:
            uuid = res.text
            print(f"Started {ticker_names} at {uuid}")
        case _:
            ClickException(f"Server returned {res.status_code}: {res.text}")


@web_socket_handler.command('stop')
@click.option(
    '--all',
    'stop_all',
    is_flag=True,
    default=False,
    help="whether to stop all web sockets"
)
@click.argument(
    'uuids',
    nargs=-1
)
@click.pass_context
def web_socket_stop(ctx, stop_all, uuids):
    """Takes multiple pids of web sockets to stop

    e.g. `nuft websocket stop 123 456`
    """
    uuids = list(uuids)
    if stop_all and uuids:
        raise ClickException("Provided uuids while using --all flag")

    if not (stop_all or uuids):
        raise ClickException("Missing uuids")

    nuft_config = ctx.obj

    path = ""
    if stop_all:
        path = f"{nuft_config.server_address}/web_sockets/stop_all"
    else:
        path = f"{nuft_config.server_address}/web_sockets/stop"

    payload = {
        "uuids": uuids
    }

    res = requests.post(path, json=payload)

    match res.status_code:
        case 200:
            print(f"Stopped {uuids if uuids else 'all websockets'}!")
        case _:
            print(f"Server returned {res.status_code}: {res.text}")
            ClickException(f"Server returned {res.status_code}: {res.text}")


@web_socket_handler.command('status')
@click.option(
    '--clear',
    is_flag=True,
    default=False,
    help="whether to remove websockets with 'failed' or 'stopped' status"
)
@click.pass_context
def web_socket_status(ctx, clear):
    headers = ['UUID', 'Ticker Names', 'Status']
    data = []

    nuft_config = ctx.obj

    if clear:
        path = f"{nuft_config.server_address}/web_sockets/status/clear"
        res = requests.post(path)

        if res.status_code != 200:
            raise ClickException(res.text)

    path = f"{nuft_config.server_address}/web_sockets/status/all"
    res = requests.get(path)

    if res.status_code != 200:
        raise ClickException(res.text)

    res_json = res.json()
    for uuid, uuid_data in res_json.items():
        ticker_names = uuid_data['tickers']
        status = uuid_data['status']

        data.append([uuid, ' '.join(ticker_names), status])

    print(tabulate(data, headers, tablefmt='outline'))


@app.group('backtest')
def backtest_handler():
    pass


@backtest_handler.command('start',
    context_settings={
        "ignore_unknown_options": True,
        "allow_extra_args": True
    },
    help="""
    Takes a mode and a keyword arguments for backtesting

    e.g. `nuft backtest start -m historical --strategy=ema`
    """
)
@click.option(
    '-m',
    '--mode',
    required=True,
    type=click.Choice(['historical', 'live'], case_sensitive=False),
    help='whether to run in historical or live data mode'
)
@click.pass_context
def backtest_start(ctx, mode):
    print(ctx.args)
    kwargs = dict([item.strip('--').split('=') for item in ctx.args])

    nuft_config = ctx.obj

    path = f"{nuft_config.server_address}/backtest/start"
    payload = {
        'mode': mode
    }
    payload.update(kwargs)

    res = requests.post(path, json=payload)

    match res.status_code:
        case 200:
            uuid = res.text
            print(f"Started backtest at {uuid}")
        case _:
            ClickException(f"Server returned {res.status_code}: {res.text}")


@backtest_handler.command('stop')
@click.option(
    '--all',
    'stop_all',
    is_flag=True,
    default=False,
    help="whether to stop all backtests"
)
@click.argument(
    'uuids',
    nargs=-1
)
@click.pass_context
def backtest_stop(ctx, stop_all, uuids):
    """Takes multiple pids of backtests to stop

    e.g. `nuft backtest stop 123 456`
    """
    uuids = list(uuids)
    if stop_all and uuids:
        raise ClickException("Provided pids while using --all flag")

    if not (stop_all or uuids):
        raise ClickException("Missing pids")

    nuft_config = ctx.obj

    path = ""
    if stop_all:
        path = f"{nuft_config.server_address}/backtest/stop_all"
    else:
        path = f"{nuft_config.server_address}/backtest/stop"

    payload = {
        "uuids": uuids
    }

    res = requests.post(path, json=payload)

    match res.status_code:
        case 200:
            print(f"Stopped {uuids if uuids else 'all backtests'}!")
        case _:
            ClickException(f"Server returned {res.status_code}: {res.text}")


@backtest_handler.command('status')
@click.option(
    '--clear',
    is_flag=True,
    default=False,
    help="whether to remove backtests with 'failed' or 'stopped' status"
)
@click.pass_context
def backtest_status(ctx, clear):
    headers = ['UUID', 'Status']
    data = []

    nuft_config = ctx.obj

    if clear:
        path = f"{nuft_config.server_address}/backtest/status/clear"
        res = requests.post(path)

        if res.status_code != 200:
            raise ClickException(res.text)

    path = f"{nuft_config.server_address}/backtest/status/all"
    res = requests.get(path)

    if res.status_code != 200:
        raise ClickException(res.text)

    res_json = res.json()
    for uuid, uuid_data in res_json.items():
        status = uuid_data['status']

        data.append([uuid, status])

    print(tabulate(data, headers, tablefmt='outline'))


def cli_run():
    app()
