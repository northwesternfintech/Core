import cement

from controllers.base import BaseController
from controllers.web_socket import WebSocketController
from controllers.backtest import BacktestController


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

    def setup(self) -> None:
        super().setup()
        # TODO: Add additional setup


if __name__ == "__main__":
    with CoreCLI() as app:
        app.run()

   
