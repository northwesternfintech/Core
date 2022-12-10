import cement
import requests

from ...mgr.utils import print_cli_error
from cement.ext.ext_argparse import ArgparseArgumentHandler
import argparse


class BaseParser(ArgparseArgumentHandler):
    class Meta:
        ignore_unknown_arguments = True


class WebSocketController(cement.Controller, BaseParser):
    class Meta:
        label = 'websocket'
        description = 'start, stop, manage websockets'
        stacked_on = 'base'
        stacked_type = 'nested'
        output_handler = 'tabulate'
        extensions = ['tabulate']

    def default(self):
        self.app.args.print_help()

    @cement.ex(
        help='lists all available websockets'
    )
    def list(self) -> None:
        print("Here are the avilable websockets!")

    @cement.ex(
        help='starts web sockets with tickers',
        arguments=[
            (['ticker_names'],
             {'help': 'name of tickers to start',
              'metavar': 'names',
              'type': str,
              'nargs': "+"})
        ]
    )
    def start(self) -> None:
        if not self.app.pargs.ticker_names:
            print_cli_error("Missing ticker names")
            return

        path = f"{self.app.server_address}/web_sockets/start"
        payload = {
            "ticker_names": self.app.pargs.ticker_names
        }

        res = requests.post(path, json=payload)
        pid = res.text

        if res.status_code == 200:
            print(f"Started {self.app.pargs.ticker_names} at {pid}")
        else:
            print_cli_error(res.text)

    @cement.ex(
        help='stops websockets',
        arguments=[
            (['--all'],
             {'help': 'stops all websockets',
              'dest': 'stop_all',
              'action': 'store_true'}),
            (['pid'],
             {'help': 'PID of websockets to stop',
              'type': str,
              'nargs': "*"})
        ]
    )
    def stop(self) -> None:
        if self.app.pargs.stop_all and self.app.pargs.pid:
            print_cli_error(f"Provided {self.app.pargs.pid} while using --all flag")
            return

        if not self.app.pargs.stop_all and not self.app.pargs.pid:
            print_cli_error("Missing pid")
            return

        path = ""
        if self.app.pargs.stop_all:
            path = f"{self.app.server_address}/web_sockets/stop_all"
        else:
            path = f"{self.app.server_address}/web_sockets/stop"

        payload = {
            "pid": self.app.pargs.pid
        }

        res = requests.post(path, json=payload)

        if res.status_code == 200:
            print(f"Stopped {self.app.pargs.pid}")
        else:
            print_cli_error(res.text)

    @cement.ex(
        help='prints status of all websockts',
        arguments=[
            (['--clear'],
             {'help': 'clears stopped/failed web sockets',
              'dest': 'clear',
              'action': 'store_true'}),
            (['args'],
             {'nargs': argparse.REMAINDER})
        ]
    )
    def status(self) -> None:
        headers = ['PID', 'Ticker Names', 'Status']
        data = []
        self.app.args.parse_args()

        print(self.app.args)
        print(self.app.pargs)
        return
        if self.app.pargs.clear:
            path = f"{self.app.server_address}/web_sockets/status/clear"
            res = requests.post(path)

            if res.status_code != 200:
                print_cli_error(res.text)
                return

        path = f"{self.app.server_address}/web_sockets/status/all"
        res = requests.get(path)

        if res.status_code != 200:
            print_cli_error(res.text)
            return

        res_json = res.json()
        for pid, pid_data in res_json.items():
            ticker_names = pid_data['tickers']
            status = pid_data['status']

            data.append([pid, ' '.join(ticker_names), status])

        self.app.render(data, headers=headers)
