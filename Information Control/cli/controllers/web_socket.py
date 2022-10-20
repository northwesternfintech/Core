import cement


class WebsocketController(cement.Controller):
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
        help='starts websockets',
        arguments=[
            (['--all'],
             {'help': 'starts all websockets',
              'dest': 'start_all',
              'action': 'store_true'}),
            (['websocket_names'],
             {'help': 'name of websockets to start',
              'metavar': 'names',
              'type': str,
              'nargs': "*"})
        ]
    )
    def start(self) -> None:
        if self.app.pargs.start_all and self.app.pargs.websocket_names:
            raise ValueError("Conflicting websockets to start")
        
        print(self.app.pargs)

        #TODO

        # Validate inputted names
        # Start web sockets

    @cement.ex(
        help='stops websockets',
        arguments=[
            (['--all'],
             {'help': 'stops all websockets',
              'dest': 'stop_all',
              'action': 'store_true'}),
            (['websocket_names'],
             {'help': 'name of websockets to stop',
              'metavar': 'names',
              'type': str,
              'nargs': "*"})
        ]
    )
    def stop(self) -> None:
        if self.app.pargs.stop_all and self.app.pargs.websocket_names:
            raise ValueError("Conflicting websockets to stop")
        
        print(self.app.pargs)

        #TODO
        # Validate inputted names
        # Stop web sockets

    @cement.ex(
        help='prints status of all websockts'
    )
    def status(self) -> None:
        headers = ['Name', 'Status']
        data = []

        print(self.app.pargs)

        # TODO
        # Actually get status data

        self.app.render(data, headers=headers)

    