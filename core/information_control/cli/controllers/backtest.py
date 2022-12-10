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
            (['--mode'],
             {'help': '"historical" or "realtime"',
              'default': 'realtime'})
        ]
    )
    def start(self) -> None:
        pass

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