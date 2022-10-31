import cement


class BacktestController(cement.Controller):
    class Meta:
        label = 'backtest'
        description = 'start, stop, manage backtesting'
        stacked_on = 'base'
        stacked_type = 'nested'
        output_handler = 'tabulate'
        extensions = ['tabulate']

    def default(self):
        self.app.args.print_help()

    @cement.ex(
        help='starts backtest',
        arguments=[
            (['algo_path'],
             {'help': 'path to algorithm to backtest',
              'metavar': 'algo-path'}),
            (['--mode'],
             {'help': '"historical" or "realtime"',
              'default': 'realtime'}),
            (['-s', '--historical-start'],
             {'help': 'start date formatted YYYY-MM-DD if --mode is "historical"',
              'default': ""}),  # TODO: Set reasonable default
            (['-e', '--historical-end'],
             {'help': 'end date formatted YYYY-MM-DD if --mode is "historical"',
             'default': ""})  # TODO: Set reasonable default
        ]
    )
    def start(self) -> None:
        print(self.app.pargs)

        VALID_MODES = ["historical", "realtime"]

        if self.app.pargs.mode not in VALID_MODES:
            raise ValueError(f"Expected valid backtest mode, received {self.app.pargs.mode}")

        # TODO

        # Start algo backtest

    @cement.ex(
        help='prints status of running backtests'
    )
    def status(self) -> None:
        headers = ['Name', 'Status']
        data = []

        print(self.app.pargs)

        # TODO
        # Actually get status data

        self.app.render(data, headers=headers)