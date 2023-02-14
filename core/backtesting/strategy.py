import matplotlib.pyplot as plt
import pandas as pd
import os
import pandas_market_calendars as mcal
from datetime import datetime, timedelta
import portfolio
import numpy as np
import time

class Strategy:
    def __init__(
        self,
        algo,
        transaction_cost=None,
        start_balance=999,
        tick_freq=1,
        tickers=None,
        name='algo',
        exchange='NYSE'
    ):
        """
        algo: the string name for the algo
        transaction_cost: float that determines the cost of every transaction
        start_balance: the balance that the strategy is starting with
        tick_freq: the number of minutes between each tick. Make sure the algo and backtester tick rates match (idk what will happen if they dont)

            Note:   if date specified is not a trading date, execute the functions on
                    the next nearest trading date
        tickers: an optional list of tickers to use for the algo (make sure it matches the one used in the algo)
        """

        self.tick_rate = tick_freq  # number of minutes between each tick

        self.start_balance = start_balance  # benchmark for visualization
        self.portfolio = portfolio.portfolio(
            starting_balance=start_balance, transaction_cost=transaction_cost
        )
        self.current_date = None  # datetime object for tracking the date in backtesting
        self.current_time = None  # datetime object for tracking hourly time
        self.name=name
        self.cal = mcal.get_calendar(exchange)
        ### Parameters for storing statistical data for strategy
        ###
        self.data = None  # the data for the current day
        self.tickdata = None  # the data for the given tick
        self.winning_action = 0
        self.total_action = 0
        self.win_rate = 0
        self.sharpe_ratio = 0
        self.prices = None
        self.tickers = \
        ['CSCO', 'UAL', 'TROW', 'ISRG', 'NVR', 'TPR', 'DVN', 'CE', 'MRO',
       'BA', 'VRTX', 'GILD', 'EQIX', 'TER', 'MDT', 'V', 'QRVO', 'A',
       'FOX', 'FLT', 'MO', 'CTRA', 'SWKS', 'ENPH', 'MCHP', 'CDNS', 'MSCI',
       'CHTR', 'EIX', 'KDP', 'BBY', 'WBA', 'LVS', 'HCA', 'AJG', 'DTE',
       'C', 'T', 'CF', 'DISH', 'MGM', 'HUM', 'CBOE', 'CFG', 'APH', 'SYY',
       'MSI', 'FCX', 'ADM', 'OGN', 'LH', 'PKI', 'LNT', 'BAC', 'LNC',
       'PSX', 'GPN', 'PPG', 'TECH', 'IRM', 'IQV', 'ESS', 'WBD', 'HAL',
       'STZ', 'DXC', 'PARA', 'ADI', 'F', 'ADBE', 'CPRT', 'TDG', 'TFX',
       'ULTA', 'ARE', 'SYK', 'CB', 'TSN', 'GNRC', 'PEP', 'PEG', 'NOW',
       'LLY', 'COST', 'REG', 'NWS', 'LOW', 'MDLZ', 'BKNG', 'ZBRA', 'FMC',
       'XEL', 'AIZ', 'MET', 'FTV', 'DLR', 'ACGL', 'XRAY', 'FAST', 'TJX',
       'SNA', 'MPC', 'BR', 'D', 'MRK', 'STX', 'NOC', 'BXP', 'KHC', 'IPG',
       'UNP', 'ALLE', 'ABBV', 'CDAY', 'ORCL', 'ECL', 'ETR', 'EBAY',
       'SBUX', 'IR', 'AMT', 'INTU', 'DPZ', 'PAYC', 'CMA', 'PG', 'CAT',
       'ODFL', 'MCD', 'MNST', 'AMZN', 'INTC', 'PNR', 'GLW', 'BDX', 'KMI',
       'CSGP', 'PWR', 'APTV', 'BBWI', 'DXCM', 'EXR', 'WELL', 'HOLX',
       'EXPD', 'GM', 'TXN', 'VRSK', 'SJM', 'TMO', 'OXY', 'RL', 'CCI',
       'MMM', 'MOS', 'FTNT', 'HSY', 'JNPR', 'DHI', 'ED', 'ES', 'ADSK',
       'GL', 'INVH', 'IP', 'EXPE', 'KO', 'PCAR', 'WDC', 'LUMN', 'PYPL',
       'NEE', 'UPS', 'ELV', 'EMR', 'MSFT', 'ANSS', 'CTAS', 'BIO', 'UDR',
       'CTLT', 'WEC', 'AME', 'IT', 'DD', 'ACN', 'VRSN', 'EW', 'CMG',
       'AWK', 'COO', 'SHW', 'HPQ', 'AMAT', 'CCL', 'MLM', 'AVY', 'AAP',
       'ATVI', 'EVRG', 'EA', 'DE', 'SPG', 'AMD', 'KLAC', 'NDAQ', 'URI',
       'WHR', 'RTX', 'NXPI', 'PNC', 'KMX', 'SEDG', 'WRK', 'MTCH', 'BIIB',
       'NVDA', 'CHRW', 'ROP', 'IDXX', 'EXC', 'HES', 'HD', 'ALB', 'VLO',
       'AON', 'ZTS', 'FDX', 'DG', 'TYL', 'HIG', 'CMS', 'CAG', 'INCY',
       'SCHW', 'HSIC', 'AZO', 'AXP', 'HPE', 'DFS', 'SEE', 'HRL', 'SO',
       'FRT', 'ZBH', 'FRC', 'CME', 'XOM', 'AMP', 'CVX', 'CMCSA', 'PCG',
       'PNW', 'ICE', 'BEN', 'UHS', 'BKR', 'EMN', 'SBAC', 'ROK', 'PTC',
       'NRG', 'NSC', 'NKE', 'FIS', 'FANG', 'VTR', 'MAS', 'RF', 'ETSY',
       'AMCR', 'TAP', 'MAR', 'XYL', 'CMI', 'MTD', 'KR', 'PLD', 'IBM',
       'USB', 'BSX', 'LKQ', 'FBHS', 'LIN', 'ITW', 'EOG', 'KMB', 'PEAK',
       'SPGI', 'NEM', 'WFC', 'CTVA', 'EL', 'GS', 'GD', 'CNP', 'PM', 'RE',
       'MCO', 'CLX', 'CAH', 'MPWR', 'DGX', 'AVB', 'DIS', 'CBRE', 'GE',
       'HII', 'LDOS', 'ALL', 'ETN', 'ALGN', 'NFLX', 'SBNY', 'LEN', 'FITB',
       'WST', 'GWW', 'TRGP', 'NTRS', 'CVS', 'AOS', 'FE', 'ABC', 'JPM',
       'ABT', 'OMC', 'COF', 'TSCO', 'PH', 'HST', 'JBHT', 'MRNA', 'TSLA',
       'MOH', 'ATO', 'COP', 'DHR', 'CNC', 'MCK', 'TXT', 'MTB', 'FDS',
       'VTRS', 'AKAM', 'ROL', 'RMD', 'WRB', 'GOOGL', 'BRO', 'ANET',
       'PAYX', 'ALK', 'DRI', 'ILMN', 'META', 'AAL', 'MAA', 'MMC', 'FOXA',
       'POOL', 'CZR', 'FFIV', 'VNO', 'CINF', 'VMC', 'MKTX', 'SRE', 'LHX',
       'ORLY', 'IVZ', 'RCL', 'PXD', 'SNPS', 'GOOG', 'EPAM', 'SIVB',
       'NDSN', 'YUM', 'EQT', 'LYV', 'PFE', 'AVGO', 'DUK', 'REGN', 'CL',
       'VFC', 'VZ', 'JCI', 'AMGN', 'TEL', 'JKHY', 'ADP', 'ON', 'STT',
       'RSG', 'IFF', 'CARR', 'TRMB', 'QCOM', 'LYB', 'GIS', 'PHM', 'ROST',
       'LUV', 'LW', 'MS', 'CPB', 'OKE', 'BK', 'J', 'SYF', 'CHD', 'HWM',
       'MHK', 'TFC', 'DAL', 'APA', 'K', 'AFL', 'CSX', 'NI', 'CPT', 'PFG',
       'NCLH', 'ZION', 'RJF', 'HBAN', 'UNH', 'PRU', 'GPC', 'WTW', 'FISV',
       'WMB', 'EQR', 'DVA', 'AIG', 'MA', 'HON', 'VICI', 'O', 'NWSA',
       'TTWO', 'AES', 'SLB', 'TT', 'TGT', 'AAPL', 'MKC', 'OTIS', 'CEG',
       'TDY', 'WY', 'APD', 'GRMN', 'AEE', 'HLT', 'DLTR', 'STE', 'HAS',
       'TMUS', 'WMT', 'NTAP', 'KIM', 'BAX', 'LMT', 'ABMD', 'KEY', 'KEYS',
       'BMY', 'PSA', 'WYNN', 'RHI', 'EFX', 'NUE', 'PKG', 'WAB', 'CTSH',
       'SWK', 'CRL', 'MU', 'TRV', 'L', 'AEP', 'CI', 'DOW', 'CDW', 'BALL',
       'JNJ', 'WM', 'DOV', 'CRM', 'PGR', 'WAT', 'IEX', 'BWA', 'LRCX',
       'NWL', 'BLK', 'PPL']
        # list of total assets in a given day at open/open
        # index maps to index of self.dates
        self.total_daily_assets_open = []
        self.total_daily_assets_close = []

        self.daily_gain_loss = []  # List of daily gain/loss indexed to self.dates
        self.monthly_gain_loss = {
            "dates": [],
            "gain_loss": [],
        }  # Dictionary of two lists / [0] -> dates / [1] -> monthly gain loss

        # the list of tickers we will be working with
        self.algo = algo
        
        benchmark_file_path = os.path.abspath(os.getcwd())
        self.benchmark = pd.read_parquet(os.path.join(benchmark_file_path,'US10yrsbond.parquet'))

    def set_algo(self,algo):
        self.algo = algo

    def back_testing(self, start_date="2022-10-19", end_date="2022-11-8"):
        """
        back_testing takes in the start and end time, then proceed to
        test the performance of the strategy

        start_time, end_time: strings in the format of "yyyy-mm-dd"
        """

        self.start_date = start_date
        self.end_date = end_date
        self.current_time = datetime.strptime(start_date, "%Y-%m-%d").replace(hour=9,minute=30)
        self.current_date = self.current_time.date()
        self.end_time = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=16)
        
        algoStartTime = time.time()
        nyse = mcal.get_calendar('NYSE')
        valid_dates = nyse.valid_days(start_date=self.start_date, end_date=self.end_date)
        self.dates = [d.to_pydatetime().date() for d in valid_dates]
        import copy; self.date_tracker = copy.deepcopy(self.dates)
        print("\n Started")
        
        
        while self.current_time < self.end_time:
            
            if self.is_trading_hour(self.current_time):            
                if self.current_time.hour == 9 and self.current_time.minute == 30:
                    self.calculate_assets('open')
                    # load today's file
                    # if an error arises just go to the next possible day (the file for the current, day doesnt exist)
                    try:
                        self.load_prices()
                    except FileNotFoundError:
                        self.current_time = self.next_nearest_trading_date(self.current_time)
                        continue
                # now self.data holds today's data as a pandas dataframe

                # simulate all the ticks for the current day

                # first find the starting time
                # the start time will be the first spot of the "time" column of the dataset
                # note that it is a datetime object so it includes the current data as well and not just the time.
                cur_time = self.current_time
                cur_time = datetime.fromisoformat(str(cur_time))

                # get the data for the current tick
                try:
                    tick_data_mask = self.data["time"] == datetime.isoformat(cur_time)
                    self.tickdata = self.data[tick_data_mask]
                except:  # if data cannot be loaded (data for the current date and time does not exist in the current loaded data)
                    break
                ticker_data_dict = {}
                
                ticker_data_dict = dict(zip(self.tickers,self.tickdata['open'].astype(float).to_list()))
                tickOrders = self.algo.update(ticker_data_dict)
                     
                tickOrders = list(tickOrders.items())
                # print(tickOrders)
                for order in tickOrders:
                    share = 0 
                    if order[1] == 'BUY': share = 1
                    else: share = -1
                    
                    # pandas built in loc function is way slower than partitioning the dataset twice
                    # df = self.data.loc[(self.data['time']==self.current_time) & (self.data['name']==order[0])]
                    
                    df = self.data[self.data['time']==self.current_time]
                    df = df[df['name']==order[0]]                    
                    if not df.empty:
                        self.portfolio.place_order(order[0], float(df['close'].iloc[0]), share)
                    else:
                        print(f"No price data for {order[0]} at {self.current_time}, skipping this order\n")
                    del df
                self.current_time += timedelta(minutes=self.tick_rate)

            else: # end of a trading day
                self.calculate_assets('close')
                self.current_time = self.next_nearest_trading_date(self.current_time)
                self.current_date = self.current_time.date()

        self.calculate_assets('close')
        self.calculate_daily_gain_loss()
        self.calculate_sharpe_ratio()

        runtime = time.time() - algoStartTime
        print("Finished")
        print("\n Runtime was %s seconds" % runtime)
        self.make_viz()

    def log(self, msg, time):
        """
        This function logs every action that the strategy has taken, from
        stock selection to buying/selling a stock
        The logs should be display alongside the curves and visualizing

        msg: a string that describes the action to be logged
        time: the time that the action took place
        """
        self.log.append([msg, time])

    def make_viz(
        self,
        directory="performance",
        plot_total_assets=True,
        plot_daily_returns=True,
        plot_monthly_returns=False,
        plot_win_rate=True,
    ):
        """
        Creates directory to save figures and logs for the back test
        """
        # Create directory for graphs

        # file_path = os.path.abspath(__file__)
        file_path = os.getcwd()
        file_path = os.path.join(file_path,'performance')

        # try making directory
        try:
            os.makedirs(file_path)
        except OSError as error:
            pass

        # Make Transaction Log
        self.make_log(file_path)
        
        file_path = os.path.join(file_path,'figures')
        fig, ax = plt.subplots(nrows=2,ncols=1)
        data = [self.daily_gain_loss, self.total_daily_assets_close]
        names = [f'daily gain loss', f'total daily assets']
        for i in range(2):
            ax[i].plot(self.dates, data[i],label=self.name)
            ax[i].set(title=names[i])
            if i == 0: # plot benchmark
                ax[i].plot(self.dates, self.benchmark['percent_change'],label='US10yrsbond')
                ax[i].legend(loc="upper right")
        fig.set_size_inches(9, 9)
        plt.savefig(file_path)
        plt.show()

    def make_log(self, file_path):
        """
        Creates a text file containing a log of the transactions of portfolio
        """
        transactions = self.portfolio.get_transactions()
        file_path_log = os.path.join(file_path,"transactions_log.txt")
        with open(file_path_log, "w+") as f:
            for i in range(len(transactions)):
                line = transactions[i]
                f.write(str(line))
                f.write("\n")
        file_path_stats = os.path.join(file_path,"statistics.txt")
        with open(file_path_stats, "w+") as f:
            f.write(
                f"The winrate of your strategy over the time interval of ({self.start_date},{self.end_date}) is {self.win_rate}\n"
            )
            f.write(f"The sharpe ratio is {self.sharpe_ratio}\n")
        return

    def load_prices(self):
        path = os.getcwd()
        path = os.path.join(path,'filtered')
        path = os.path.join(path,f'{self.current_time.date().strftime("%Y-%m-%d")}.parquet')
        self.data = pd.read_parquet(path)

    def calculate_assets(self, mode): # mode can be open or close
        total_holdings = 0
        balance = self.portfolio.get_balance()  # current balance of the portfolio
        holdings = self.portfolio.get_holdings()  # current holdings of the portfolio
        
        for h in holdings:
            # str_time = self.current_time.strftime("%Y-%m-%d %H:%M:%S")
            partial_data = self.data[self.data["name"] == h[0]]
            partial_data =  self.data[self.data["time"] == self.current_time]
            if not partial_data.empty:
                curr_price = float(partial_data['close'])
                # increment the running sum of total by the number of holdings by the current price of holding
                total_holdings += h[1] * curr_price
            
        if mode == 'open':
            self.total_daily_assets_open.append(total_holdings + balance)
        else:
            self.total_daily_assets_close.append(total_holdings + balance)


    def calculate_total_assets(self, data_column="close"):
        """
        calculate the total amount of assets in a portfolio at the selected time each
        day.

        Should be run during backtesting for each iteration.

        data_column: a string that describes which column the data is from
        """
        total_holdings = 0  # running sum of total sum of assets in holdings
        balance = self.portfolio.get_balance()  # current balance of the portfolio
        holdings = self.portfolio.get_holdings()  # current holdings of the portfolio

        data = self.data  # pandas dataframe of stock data

        for h in holdings:

            # get the price of the holdings at the current date
            partial_data = data[data["name"] == h[0] and data["date"] == self.current_time]
            curr_price = float(partial_data[data_column])

            # increment the running sum of total by the number of holdings by the current price of holding
            total_holdings += h[1] * curr_price

        return (
            total_holdings + balance
        )  # total assets is the sum of holdings and balance

    def calculate_daily_gain_loss(self):
        """
        Calculate the daily gain/loss based from open-close (daily gain/loss = (close - open) / open)
        """
        day_open = self.total_daily_assets_open
        day_close = self.total_daily_assets_close
        # Calculate the daily gain/loss for each day
        self.daily_gain_loss = [0] * len(day_close)
        for i in range(len(self.total_daily_assets_open)):
            self.daily_gain_loss[i] = (day_close[i] - day_open[i]) / day_open[i]
        
        

    def calculate_monthly_gain_loss(self):
        """
        Calculate the monthly gain/loss based from open-close

        Maybe month to date?
        """
        self.monthly_gain_loss["dates"].append(self.dates[0])
        self.monthly_gain_loss["gain_loss"].append(0)

        curr_data = self.total_daily_assets_open[0]
        prev_data = self.total_daily_assets_open[0]

        for i in range(len(self.dates)):
            # If first of month
            if self.dates[i].day == 1:
                curr_data = self.total_daily_assets_open[i]
                self.monthly_gain_loss["dates"].append(self.dates[i])
                self.monthly_gain_loss["gain_loss"].append(
                    (curr_data - prev_data) / prev_data
                )
                prev_data = curr_data

        return

    def calculate_win_rate(self):
        """
        Calculate and store count for total actions, winning actions, and win rate
        """

        total_action_count = (
            0  # Variable that keeps track of total actions undertaken by strategy
        )
        winning_action_count = (
            0  # Variables that keeps track of winning actions undertaken by strategy
        )

        transactions = self.portfolio.transactions

        for t in transactions:
            # Only 'sell' transactions can be considered for win/loss
            if t[0] == "sell":
                total_action_count += 1

                # Check if transaction is profitable
                if t[4] > 0:
                    winning_action_count += 1

        self.total_action = (
            total_action_count  # Update the total_action parameter in strategy
        )
        self.winnning_action = (
            winning_action_count  # update the wining_action parameter in strategy
        )

        if self.total_action == 0:
            return None  # stop if no action has been made

        self.win_rate = (
            winning_action_count / total_action_count
        )  # Update the win_rate parameter in strategy

        return True

    def calculate_sharpe_ratio(self):
        # E[Returns - Riskfree Returns]/standard deviation of excess return
        # Benchmark/RiskReturns
        if len(self.daily_gain_loss) == 0:
            raise ValueError("Empty data for daily gain/loss")
        
        str_dates = [d.strftime("%Y-%m-%d") for d in self.dates]
        self.benchmark['percent_change'] = self.benchmark['Close'].pct_change(axis='rows')
        self.benchmark = self.benchmark.set_index('Date')
        self.benchmark = self.benchmark[self.benchmark.index.isin(str_dates)]
        assert len(self.daily_gain_loss) == len(
            self.benchmark
        ), "Number of benchmark values does not match number of values in daily gain/loss."

        return_differentials = [0] * len(self.daily_gain_loss)
        
        benchmark_data = self.benchmark['percent_change'].to_list()
        for i in range(len(self.daily_gain_loss)):
            return_differentials[i] = self.daily_gain_loss[i] - benchmark_data[i]
        return_differentials = np.array(return_differentials)
        expected_differential = np.mean(return_differentials)
        std = np.std(np.array(self.daily_gain_loss))
        if std == 0:
            self.sharpe_ratio = 0
            return False
        self.sharpe_ratio = expected_differential / std
        return True

    def is_trading_hour(self, d):
        """
        Verify if the given date is a trading day, return boolean
        Should only be called by back_testing()

        date: datetime object
        """
        if (d.hour > 9 and d.hour < 16 or (d.hour == 9\
            and d.minute >= 30)) and d.date() in self.dates:
                return True
        else: return False

    def is_trading_date(self, d):
        return d.date() in self.dates
            
    def next_nearest_trading_date(self, d):
        """
        Return the next nearest trading date as a datetime object
        Should only be called by back_testing()
        date: datetime object
        """
        self.date_tracker.pop(0)  
        d = self.date_tracker[0]  
        print(f"{len(self.dates)-len(self.date_tracker)}/{len(self.dates)}")
        return datetime(d.year, d.month, d.day, 9, 30)

import dummy


s = Strategy(
    algo=None,
    transaction_cost=0.0001,
    start_balance=10000,
    name='test'
)


d = dummy.dummy()
s.set_algo(d)

s.back_testing()
