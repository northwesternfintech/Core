import os

import cement

from controllers.backtest import BacktestController
from controllers.base import BaseController
from controllers.web_socket import WebSocketController

DIR_HOME = os.path.expanduser('~')
DIR_NUFT = os.path.join(DIR_HOME, '.nuft')
# DIR_LOG = os.path.join(DIR_NUFT, 'logs')


class CoreCLI(cement.App):
    class Meta:
        label = "nuft"
        extensions = ['tabulate']
        output_handler = 'tabulate'
        config_files = [
            os.path.join(DIR_NUFT, "creds.conf")
        ]
        handlers = [
            BaseController,
            WebSocketController,
            BacktestController
        ]

    def setup(self) -> None:
        super().setup()
        # TODO: Add additional setup


def main():
    if not os.path.exists(DIR_NUFT):
        os.makedirs(DIR_NUFT, exist_ok=True)

        with open(os.path.join(DIR_NUFT, "creds.conf"), "w"):
            pass  # TODO: Add reasonable default

    with CoreCLI() as app:
        app.run()


if __name__ == "__main__":
    main()

   
