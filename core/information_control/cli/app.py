import os

import cement

from .controllers.backtest import BacktestController
from .controllers.base import BaseController
from .controllers.web_socket import WebSocketController

DIR_HOME = os.path.expanduser('~')
DIR_NUFT = os.path.join(DIR_HOME, '.nuft')
# DIR_LOG = os.path.join(DIR_NUFT, 'logs')


class CoreCLI(cement.App):
    class Meta:
        label = "nuft"
        extensions = ['tabulate']
        output_handler = 'tabulate'
        handlers = [
            BaseController,
            WebSocketController,
            BacktestController
        ]

        config_files = [
            os.path.join(DIR_NUFT, "config.ini")
        ]

        config_defaults = {
            'server': {
                'host': '127.0.0.1',
                'port': 5000
            },
            'interchange': {
                'host': '127.0.0.1',
                'pub_port': 50001,
                'sub_port': 50002
            },
            'paths': {
            
            },
            'logging': {
            
            },
            'data_acquision': {

            },
            'backtest': {

            },
            'execution': {

            }
        }

    def setup(self) -> None:
        super().setup()

        for section in self.config.get_sections():
            self.config.remove_section(section)

        self.nuft_dir = os.path.join(DIR_HOME, '.nuft')
        self.conf_path = os.path.join(self.nuft_dir, "config.ini")

        self.config.read_dict(self._meta.config_defaults)

        if not os.path.exists(self.conf_path):
            with open(self.conf_path, 'w') as f:
                self.config.write(f)
        else:
            with open(self.conf_path, 'r') as f:
                self.config.read_file(f)

        server_host = self.config.get('server', 'host')
        server_port = self.config.get('server', 'port')
        self.server_address = f"http://{server_host}:{server_port}"


def main():
    if not os.path.exists(DIR_NUFT):
        os.makedirs(DIR_NUFT, exist_ok=True)

        with open(os.path.join(DIR_NUFT, "config.ini"), "w"):
            pass  # TODO: Add reasonable default

    with CoreCLI() as app:
        app.run()


if __name__ == "__main__":
    main()