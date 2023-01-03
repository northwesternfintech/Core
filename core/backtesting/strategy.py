import matplotlib.pyplot as plt
import pandas as pd
import os
import shutil
# import pyarrow as pa
# import pyarrow.parquet as pq

import holidays
from datetime import datetime, timedelta
import portfolio
import numpy as np
import time

# imports for algorithms we've made
import BollingerBandsMultiStock


class Strategy:
    def __init__(
        self,
        algo,
        transaction_cost=None,
        start_balance=None,
        tick_freq=1,
        data_file_folder="filtered",
        benchmark_file_path=None,
        tickers=None,
        name='algo',
    ):
        """
        algo: the string name for the
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
        self.open_close = (
            None  # a boolean for tracking if it's currently market open/close
        )
        self.name=name
        # True for open and False for close
        self.nyse_holidays = (
            holidays.NYSE()
        )  # a dictionary storing all stock market holidays
        self._data_file_folder = data_file_folder
        ##self.data = pd.read_csv(self._data_file_folder) csv reading is outdated
        ###
        ### Parameters for storing statistical data for strategy
        ###
        self.data = None  # the data for the current day
        self.tickdata = None  # the data for the given tick
        self.winning_action = 0
        self.total_action = 0

        self.win_rate = 0

        self.sharpe_ratio = 0

        self.prices = None

        # list of total assets in a given day at open/open
        # index maps to index of self.dates
        self.total_daily_assets_open = []
        self.total_daily_assets_close = []

        self.daily_gain_loss = []  # List of daily gain/loss indexed to self.dates
        self.monthly_gain_loss = {
            "dates": [],
            "gain_loss": [],
        }  # Dictionary of two lists / [0] -> dates / [1] -> monthly gain loss

        self.dates = (
            []
        )  # list of dates / index maps to index of self.total_daily_assets

        # the list of tickers we will be working with
        self.tickers = ["CSCO","UAL","TROW","ISRG","NVR","TPR","DVN","CE","MRO","BA","VRTX","GILD","EQIX","TER","MDT","V","QRVO","A","FOX","FLT","MO","CTRA","SWKS","ENPH","MCHP","CDNS","MSCI","CHTR","EIX","KDP","BBY","GEN","WBA","LVS","HCA","AJG","DTE","C","T","CF","DISH","MGM","HUM","CBOE","CFG","APH","SYY","MSI","FCX","ADM","OGN","LH","PKI","LNT","BAC","LNC","PSX","GPN","PPG","TECH","IRM","IQV","ESS","WBD","HAL","STZ","DXC","PARA","ADI","F","ADBE","CPRT","TDG","TFX","ULTA","ARE","SYK","CB","TSN","GNRC","PEP","PEG","NOW","LLY","COST","REG","NWS","LOW","MDLZ","BKNG","ZBRA","FMC","XEL","AIZ","MET","FTV","DLR","ACGL","XRAY","FAST","TJX","SNA","MPC","BR","D","MRK","STX","NOC","BXP","KHC","IPG","UNP","ALLE","ABBV","CDAY","ORCL","ECL","ETR","EBAY","SBUX","IR","AMT","INTU","DPZ","PAYC","CMA","PG","CAT","ODFL","MCD","MNST","AMZN","INTC","PNR","GLW","BDX","KMI","CSGP","PWR","APTV","BBWI","DXCM","EXR","WELL","HOLX","EXPD","GM","TXN","VRSK","SJM","TMO","OXY","RL","CCI","MMM","MOS","FTNT","HSY","JNPR","DHI","ED","ES","ADSK","GL","INVH","IP","EXPE","KO","PCAR","WDC","LUMN","PYPL","NEE","UPS","ELV","EMR","MSFT","ANSS","CTAS","BIO","UDR","CTLT","WEC","AME","IT","DD","ACN","VRSN","EW","CMG","AWK","COO","SHW","HPQ","AMAT","CCL","MLM","AVY","AAP","ATVI","EVRG","EA","DE","SPG","AMD","KLAC","NDAQ","URI","WHR","RTX","NXPI","PNC","KMX","SEDG","WRK","MTCH","BIIB","NVDA","CHRW","ROP","IDXX","EXC","HES","HD","ALB","VLO","AON","ZTS","FDX","DG","TYL","HIG","CMS","CAG","INCY","SCHW","HSIC","AZO","AXP","HPE","DFS","SEE","HRL","SO","FRT","ZBH","FRC","CME","XOM","AMP","CVX","CMCSA","PCG","PNW","ICE","BEN","UHS","BKR","EMN","SBAC","ROK","PTC","NRG","NSC","NKE","FIS","FANG","VTR","MAS","RF","ETSY","AMCR","TAP","MAR","XYL","CMI","MTD","KR","PLD","IBM","USB","BSX","LKQ","FBHS","LIN","ITW","EOG","KMB","PEAK","SPGI","NEM","WFC","CTVA","EL","GS","GD","CNP","PM","RE","MCO","CLX","CAH","MPWR","DGX","AVB","DIS","CBRE","GE","HII","LDOS","ALL","ETN","ALGN","NFLX","SBNY","LEN","FITB","WST","GWW","TRGP","NTRS","CVS","AOS","FE","ABC","JPM","ABT","OMC","COF","TSCO","PH","HST","JBHT","MRNA","TSLA","MOH","ATO","COP","DHR","CNC","MCK","TXT","MTB","FDS","VTRS","AKAM","ROL","RMD","WRB","GOOGL","BRO","ANET","PAYX","ALK","DRI","ILMN","META","AAL","MAA","MMC","FOXA","POOL","CZR","FFIV","VNO","CINF","VMC","MKTX","SRE","LHX","ORLY","IVZ","RCL","PXD","SNPS","GOOG","EPAM","SIVB","NDSN","YUM","EQT","LYV","PFE","AVGO","DUK","REGN","CL","VFC","VZ","JCI","AMGN","TEL","JKHY","ADP","ON","STT","RSG","IFF","CARR","TRMB","QCOM","LYB","GIS","PHM","ROST","LUV","LW","MS","CPB","OKE","BK","J","SYF","CHD","HWM","MHK","TFC","DAL","APA","K","AFL","CSX","NI","CPT","PFG","NCLH","ZION","RJF","HBAN","UNH","PRU","GPC","WTW","FISV","WMB","EQR","DVA","AIG","MA","HON","VICI","O","NWSA","TTWO","AES","SLB","TT","TGT","AAPL","MKC","OTIS","CEG","TDY","WY","APD","GRMN","AEE","HLT","DLTR","STE","HAS","TMUS","WMT","NTAP","KIM","BAX","LMT","ABMD","KEY","KEYS","BMY","PSA","WYNN","RHI","EFX","NUE","PKG","WAB","CTSH","SWK","CRL","MU","TRV","L","AEP","CI","DOW","CDW","BALL","JNJ","WM","DOV","CRM","PGR","WAT","IEX","BWA","LRCX","NWL","BLK","PPL"]
        
        self.algo = algo.BollingerBandsMultiStock(tickers=self.tickers,
                                                  MAL=20,
                                                  bandSD=2,
                                                  dayConst=390,
                                                  clearDataLen=10000)
        benchmark_file_path = os.path.abspath(os.getcwd())
        benchmark_file_path = os.path.join(benchmark_file_path,'backtesting')
        self.benchmark = pd.read_csv(os.path.join(benchmark_file_path,'US10yrsbond.csv'))


    def back_testing(self, start_date="2022-10-19", end_date="2022-10-21"):
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
        self.load_prices()
        print("\n started backtesting")
        
        while self.current_time < self.end_time:
            print(self.current_time)
            if self.is_trading_hour(self.current_time):            
                if self.current_time.hour == 9 and self.current_time.minute == 30:
                    self.calculate_assets('open')
                    self.dates.append(self.current_date)
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
                if self.tickers == None:
                    self.tickers = self.data["name"].unique()
                    
                ticker_data_dict = dict(zip(self.tickers,self.tickdata['open'].to_list()))
                tickOrders = self.algo.update(ticker_data_dict)
                        
                self.current_time += timedelta(minutes=self.tick_rate)

            else: # end of a trading day
                self.calculate_assets('close')
                self.current_time = self.next_nearest_trading_date(self.current_time)
                self.current_date = self.current_time.date()
                # load next day's file
                # if an error arises just go to the next possible day (the file for the current, day doesnt exist)
                try:
                    self.load_prices()
                except FileNotFoundError:
                    self.current_time = self.next_nearest_trading_date(self.current_time)
                    continue
                
        self.calculate_assets('close')
        self.calculate_daily_gain_loss()

        self.calculate_win_rate()
        self.calculate_sharpe_ratio()

        runtime = time.time() - algoStartTime
        print("\n finished backtesting, started visualizing")
        print("\n Runtime was %s seconds" % runtime)
        self.make_viz()
        file_path = os.getcwd()
        file_path = os.path.join('backtesting')
        file_path = os.path.join(file_path, "backtesting_results")

    def log(self, msg, time):
        """
        This function logs every action that the strategy has taken, from
        stock selection to buying/selling a stock
        The logs should be display alongside the curves and visualizing

        msg: a string that describes the action to be logged
        time: the time that the action took place
        """
        self.log.append([msg, time])

    def fetch_viz(
        self, plot_total_assets=True, plot_daily_returns=True, plot_win_rate=True
    ):
        """
        This function should be executed after backtesting for visualizing the
        performance of the strategy
        Use matplotlibe/seaborn/etc. to make graphs, then display the logs by the
        side, gotta make this look fancy
        Fetches the graphs and logs from the saved directory

        Boolean parameters gives user control over which variables to display

        plot_total_assets: a boolean that indicates whether total_assets should be displayed
        plot_daily_returns: a boolean that indicates whether daily_returns should be displayed
        plot_win_rate: a boolean that indicates whether win_rate should be displayed
        """

        pass

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
        file_path = os.path.join(file_path,'backtesting')
        file_path = os.path.join(file_path, directory)

        # try making directory
        try:
            os.makedirs(file_path)
        except OSError as error:
            print("directory already exists", error)

        # Make Transaction Log
        self.make_log(file_path)

        # Make graphs
        if plot_total_assets:
            # plot self.total_daily_assets vs self.dates with create_plot()
            self.make_plot(
                x_data=self.dates,
                y_data=self.total_daily_assets_open,
                file_path=file_path,
                xlabel="Dates",
                ylabel="Total Daily Assets (USD)",
                title=f'{self.current_date.strftime("%Y-%m-%d")}_total_daily_assets',
            )
        if plot_daily_returns:
            # plot self.daily_gain_loss vs self.dates with create_plot()
            self.make_plot(
                x_data=self.dates,
                y_data=self.daily_gain_loss,
                file_path=file_path,
                xlabel="Dates",
                ylabel="Percentage Change Assets",
                title=f'{self.name}_{self.start_date}_{self.end_date}_daily_return',
                plot_together=self.benchmark,
            )

        if plot_monthly_returns:
            # plot self.daily_gain_loss vs self.dates with create_plot()
            self.make_plot(
                x_data=self.monthly_gain_loss["dates"],
                y_data=self.monthly_gain_loss["gain_loss"],
                file_path=file_path,
                xlabel="Dates",
                ylabel="Percentage Change Assets",
                title=f'{self.current_date.strftime("%Y-%m-%d")}_monthly_gain_loss',
            )
            
        # print(self.benchmark)
        # self.make_plot(x_data=self.dates, y_data=self.benchmark, file_path=file_path,
        #                     xlabel='Dates', ylabel='10 yr bond price',
        #                     title=f'{self.current_date.strftime("%Y-%m-%d")} 10 yr bond')
        return

    def make_log(self, file_path):
        """
        Creates a text file containing a log of the transactions of portfolio
        """
        transactions = self.portfolio.get_transactions()
        with open(file_path + "/transactions_log.txt", "w+") as f:
            for i in range(len(transactions)):
                line = transactions[i]
                f.write(line[0], line[1], line[2], line[3])
                f.write("\n")

        with open(file_path + "/statistics.txt", "w+") as f:
            f.write(
                f"The winrate of your strategy over the time interval of ({self.start_date},{self.end_date}) is {self.win_rate}\n"
            )
            f.write(f"The sharpe ratio is {self.sharpe_ratio}\n")
        return

    def make_plot(
        self, x_data, y_data, title, xlabel, ylabel, file_path, plot_together=False
    ):
        """
        Creates PNGs of plots given the data and axis.
        """
        # print(x_data)
        # print(y_data)
        # date_time = self.dates
        # date_time = pd.to_datetime(date_time)

        plt.plot(x_data, y_data)

        plt.xlabel(xlabel,labelpad=7)
        plt.ylabel(ylabel,labelpad=7)
        plt.title(title)

        plot_name = f"{file_path}/{title}_plot.png"
                
        plt.savefig(plot_name)
        plt.clf()
        return

    def load_prices(self):
        path = os.getcwd()
        path = os.path.join(path,'backtesting')
        path = os.path.join(path,'filtered')
        path = os.path.join(path,f'{self.current_date}.parquet')
        self.data = pd.read_parquet(path)

    def get_total_assets(self):
        return [self.total_daily_assets_open, self.total_daily_assets_close]

    def get_daily_gain_loss(self):
        return self.daily_gain_loss

    def get_monthly_gain_loss(self):
        return self.monthly_gain_loss

    def get_win_rate(self):
        return [self.win_rate, self.winning_action, self.total_action]

    def calculate_assets(self, mode): # mode can be open or close
        total_holdings = 0
        balance = self.portfolio.get_balance()  # current balance of the portfolio
        holdings = self.portfolio.get_holdings()  # current holdings of the portfolio
        
        for h in holdings:

            # get the price of the holdings at the current date
            str_time = self.current_time.strftime("%Y-%m-%d %H:%M:%S")
            partial_data = self.data[self.data["name"] == h[0] and self.data["time"] == str_time]
            curr_price = float(partial_data[mode])

            # increment the running sum of total by the number of holdings by the current price of holding
            total_holdings += h[1] * curr_price
            
        if mode == 'open':
            self.total_daily_assets_open.append(total_holdings + balance)
        else:
            self.total_daily_assets_close.append(total_holdings + balance)


    def calculate_total_assets(self, data_column="open"):
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
            str_date = self.current_date.strftime("%Y-%m-%d")
            partial_data = data[data["Name"] == h[0] and data["date"] == str_date]
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
        # Benchmark/RiskReturns S&P
        if len(self.daily_gain_loss) == 0:
            raise ValueError("Empty data for daily gain/loss")

        # update benchmark every virtual day
        mask1 = (self.benchmark['Date'] >= self.start_date)
        mask2 = (self.benchmark['Date'] <= self.end_date)
        mask = mask1 & mask2
        self.benchmark = self.benchmark[mask]
        assert len(self.daily_gain_loss) == len(
            self.benchmark
        ), "Number of benchmark values does not match number of values in daily gain/loss."

        return_differentials = [0] * len(self.daily_gain_loss)
        
        benchmark_data = self.benchmark['Close'].to_list()
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

    def is_trading_hour(self, date):
        """
        Verify if the given date is a trading day, return boolean
        Should only be called by back_testing()

        date: datetime object
        """
        if (date.hour > 9 and date.hour < 16 or (date.hour == 9\
            and date.minute >= 30)) and not date in self.nyse_holidays:
                return True
        else: return False

    def is_trading_date(self, date):
        return not date.date() in self.nyse_holidays
            
    def next_nearest_trading_date(self, d):
        """
        Return the next nearest trading date as a datetime object
        Should only be called by back_testing()

        date: datetime object
        """
        print(d)
        d += timedelta(days=1)  # move onto next date
        d = d.replace(hour=9, minute=30)
        while not self.is_trading_date(d):  # check if current date is trading date
            d += timedelta(days=1)  # move onto next date
            d = d.replace(hour=9, minute=30)
        return d

    def handle_run_daily(self):
        """
        handler for run_daily, to be called in back_testing()
        """
        self.on_market_open()
        self.run_daily()
        self.on_market_close()

    def place_order(self, stock_name, shares):
        """
        handler for buy/sell, set shares > 0 for buy and < 0 for sell
        this function should be called by users in the followed functions only

        stock_name: string
        shares: float
        """
        stock_price = self.data["date" == self.current_date & "Name" == stock_name]
        if self.current_date:
            stock_price = stock_price["open"]
        else:
            stock_price = stock_price["close"]
        self.portfolio.place_order(stock_name, stock_price, shares)

    ################################################################################
    # below are methods that the designer of strategy should override
    # developlers shouldn't modified anything below this line
    ################################################################################
    ################################################################################

    def on_market_close(self):
        """
        This method should be overided by the designer of strategy on an instance level
        with python's type package
        Should be executed before market close everyday
        """
        # should be used for placing at-the-close orders and stock selection
        pass

    def on_market_open(self):
        """
        This method should be overided by the designer of strategy on an instance level
        with python's type package
        Should be executed before market open every virtual day
        """
        # should be used for placing at-the-close orders and stock selection
        pass

    def run_tickly(self):
        """
        This method is overided by the designer. Executed on each tick. By default each minute.
        """
        pass

    def run_hourly(self):
        """
        Overrided by the designer, executes at the first instance where the hour changes from one hour to the next (i.e., 9AM to 10AM)
        """
        pass

    def run_daily(self):
        """
        This method should be overided by the designer of strategy on an instance level
        with python's type package
        Should be executed before market open every virtual day
        """
        pass

    def run_weekly(self):
        """
        This method should be overided by the designer of strategy on an instance level
        with python's type package
        Should be executed before market open every virtual week on the day specified (or Mon as default)
        If date specified is not a trading date, then find the next nearest trading date
        """
        pass

    def run_monthly(self):
        """
        This method should be overided by the designer of strategy on an instance level
        with python's type package
        Should be executed before market open every virtual month on the day specified (or 1st as default)
        If date specified is not a trading date, then find the next nearest trading date
        """
        pass


import BollingerBandsMultiStock

s = Strategy(
    algo=BollingerBandsMultiStock,
    transaction_cost=0.05,
    start_balance=10000,
    data_file_folder="filtered",
    name='BollingerBandsMultiStock'
)

s.back_testing()
