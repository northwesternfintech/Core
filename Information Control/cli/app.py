import cement

from controllers.base import BaseController
from controllers.web_socket import WebsocketController


class CoreCLI(cement.App):
    class Meta:
        label = "nuft"
        extensions = ['tabulate']
        output_handler = 'tabulate'
        handlers = [
            BaseController,
            WebsocketController
        ]

    def setup(self) -> None:
        super().setup()
        # TODO: Add additional setup

with CoreCLI() as app:
    app.run()

   
