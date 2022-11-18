import matplotlib.pyplot as plt
import pandas as pd
import os
import shutil

import holidays
from datetime import datetime, timedelta
import portfolio
import numpy as np
import time

class BackTester:
    
    def __init__(self, data_file_path=None):
        # init a backtester, retrieve data from local file
        # data are stored as a pd dataframe that has the following cols
        # date; open; high; low; close; volume; Name
        self._data_file_path = data_file_path or 'data/2013-2018.csv'
        self.data = pd.read_csv(self._data_file_path)
                    
class Strategy(BackTester):
    
    def __init__(self, transaction_cost=None, start_balance=None, week_day=None, month_day=None): 
        '''
        transaction_cost: float that determines the cost of every transaction
        start_balance: the balance that the strategy is starting with
        
        week_day:   every week, when it comes to the week_day specified, execute
                    the run_weekly function. Default is Monday.
        month_day:  every month, when it comes to the month_day specified, execute
                    the run_monthly function. Default is 1st.
            Note:   if date specified is not a trading date, execute the functions on 
                    the next nearest trading date
        '''
        self.start_balance = start_balance # benchmark for visualization
        self.portfolio = portfolio.portfolio(starting_balance = start_balance, 
                                   transaction_cost = transaction_cost)
        self.current_time = None    # datetime object for tracking the date in backtesting
        self.open_close = None      # a boolean for tracking if it's currently market open/close
                                    # True for open and False for close
        self.nyse_holidays = holidays.NYSE() # a dictionary storing all stock market holidays

        ###
        ### Parameters for storing statistical data for strategy
        ###

        self.winning_action = 0
        self.total_action = 0

        self.win_rate = 0

        self.sharpe_ratio = 0
        
        self.prices = None

        # list of total assets in a given day at open/open
        # index maps to index of self.dates
        self.total_daily_assets_open = [] 
        self.total_daily_assets_close = []

        self.daily_gain_loss = [] # List of daily gain/loss indexed to self.dates
        self.monthly_gain_loss = {'dates': [], 'gain_loss':[]} # Dictionary of two lists / [0] -> dates / [1] -> monthly gain loss

        self.dates = [] # list of dates / index maps to index of self.total_daily_assets

        self.week_day = week_day # Integer with monday as 0 and sunday as 6
        self.month_day = month_day # Number from 1 to 31

    def back_testing(self, start_time=None, end_time=None):
        '''
        back_testing takes in the start and end time, then proceed to 
        test the performance of the strategy
        
        start_time, end_time: strings in the format of "yyyy-mm-dd"
        '''
        start = start_time or '2013-03-28'
        end = end_time or '2018-02-05'

        self.current_time = datetime.strptime(start, "%Y-%m-%d").date()
        end_time = datetime.strptime(end, "%Y-%m-%d").date()
        
        algoStartTime = time.time()
        print('\n started backtesting')
        while self.current_time != end_time:
            self.load_prices()
            if(self.is_trading_date(self.current_time)): 
                self.run_daily()
                if(self.week_day == self.current_time.weekday()): 
                    self.run_weekly()
                if(self.month_day == self.current_time.day()): 
                    self.run_monthly()
                self.current_time += datetime.timedelta(days=1)

            else:
                self.current_time = self.next_nearest_trading_date()
        

            # Run daily/weekly/monthly
            
            # append total amount of assets to self.total_daily_assets_open
            # append total amount of assets to self.total_daily_assets_close

            
            
        # Calculate statistical data
        # Calculating Sharpe Ratio

        runtime = algoStartTime - time.time()
        print('\n finished backtesting, started visualizing')
        print('\n Runtime was %s seconds' % runtime)
        self.make_viz()
        file_path = os.getcwd()
        file_path = os.path.join(file_path, 'backtester')
        self.make_log(file_path)
        #save the log as a txt
    
    def load_prices(self):
        date = f'{self.current_time.year}-{self.current_time.month}-{self.current_time.day}'
        self.prices = self.data[self.data['date'] == date]
        
    def benchmark(self):
        '''
        returns benchmark data for statistic calculations in the form of a list. 
        Specifically returns the 'returns' of the benchmark for each day
        '''
        pass

    def log(self, msg, time): 
        '''
        This function logs every action that the strategy has taken, from
        stock selection to buying/selling a stock
        The logs should be display alongside the curves and visualizing
        
        msg: a string that describes the action to be logged
        time: the time that the action took place
        '''
        self.log.append([msg, time])
    
    def fetch_viz(self, plot_total_assets=True, plot_daily_returns=True, plot_win_rate=True): 
        '''
        This function should be executed after backtesting for visualizing the 
        performance of the strategy
        Use matplotlibe/seaborn/etc. to make graphs, then display the logs by the 
        side, gotta make this look fancy
        Fetches the graphs and logs from the saved directory

        Boolean parameters gives user control over which variables to display

        plot_total_assets: a boolean that indicates whether total_assets should be displayed
        plot_daily_returns: a boolean that indicates whether daily_returns should be displayed
        plot_win_rate: a boolean that indicates whether win_rate should be displayed
        '''

        pass

    def make_viz(self, directory='backtester', plot_total_assets=True, plot_daily_returns=True, plot_monthly_returns=True, plot_win_rate=True): 
        '''
        Creates directory to save figures and logs for the back test
        '''
        # Create directory for graphs
        
        # file_path = os.path.abspath(__file__)
        file_path = os.getcwd()
        file_path = os.path.join(file_path, directory)

        # try making directory
        try:
            os.makedirs(file_path)
        except OSError as error:
            print("Could not create directory:", error)

        # Make Transaction Log
        self.make_log(file_path)

        # Make graphs
        if(plot_total_assets):
            # plot self.total_daily_assets vs self.dates with create_plot()
            self.make_plot(x_data=self.dates, y_data=self.total_daily_assets_open, file_path=file_path, 
                            xlabel='Dates', ylabel='Total Daily Assets (USD)', 
                            title=f'{self.current_time.strftime("%Y-%m-%d")}_total_daily_assets')
        if(plot_daily_returns):
            # plot self.daily_gain_loss vs self.dates with create_plot()
            self.make_plot(x_data=self.dates, y_data=self.daily_gain_loss, file_path=file_path,
                            xlabel='Dates', ylabel='Percentage Change Assets', 
                            title=f'{self.current_time.strftime("%Y-%m-%d")}_daily_gain_loss')

        if(plot_monthly_returns):
            # plot self.daily_gain_loss vs self.dates with create_plot()
            self.make_plot(x_data=self.monthly_gain_loss['dates'], y_data=self.monthly_gain_loss['gain_loss'], file_path=file_path,
                            xlabel='Dates', ylabel='Percentage Change Assets', 
                            title=f'{self.current_time.strftime("%Y-%m-%d")}_monthly_gain_loss')

        return

    def make_log(self, file_path): 
        '''
        Creates a text file containing a log of the transactions of portfolio
        '''

        transactions = self.portfolio.get_transactions()

        with open(file_path + 'transactions_log.txt', 'w') as f:
            for i in range(len(transactions)):
                line = transactions[i]
                f.write(line[0], line[1], line[2], line[3])
                f.write('\n')

        return

    def make_plot(self, x_data, y_data, title, xlabel, ylabel, file_path): 
        '''
        Creates PNGs of plots given the data and axis.
        '''
            
        # date_time = self.dates
        # date_time = pd.to_datetime(date_time)

        df = pd.DataFrame()
        df['x'] = x_data
        df['y'] = y_data
        df = df.set_index('x')
        plt.plot(df)

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()

        plot_name = f'{file_path}/{title}_plot.png'

        plt.savefig(plot_name)

        return

    def update_testing_data(self):
        '''
        Updates the testing data for information that cannot be gathered after
        backtesting is completed
        '''
        self.total_daily_assets_open.append(self.calculate_total_assets(data_column='open'))
        self.total_daily_assets_close.append(self.calculate_total_assets(data_column='close'))

        self.dates.append(self.current_time)

    def get_total_assets(self): return [self.total_daily_assets_open, self.total_daily_assets_close]

    def get_daily_gain_loss(self): return self.daily_gain_loss

    def get_monthly_gain_loss(self): return self.monthly_gain_loss

    def get_win_rate(self): return [self.win_rate, self.winning_action, self.total_action]

    def calculate_total_assets(self, data_column='open'):
        '''
        calculate the total amount of assets in a portfolio at the selected time each
        day.

        Should be run during backtesting for each iteration.

        data_column: a string that describes which column the data is from
        '''
        total_holdings = 0 # running sum of total sum of assets in holdings
        balance = self.portfolio.get_balance() # current balance of the portfolio
        holdings = self.portfolio.get_holdings() # current holdings of the portfolio
        
        data = self.data # pandas dataframe of stock data

        for h in holdings:

            # get the price of the holdings at the current date
            str_date = self.current_time.strftime("%Y-%m-%d")
            partial_data = data[data['Name']==h[0] and data['date']==str_date]
            curr_price = float(partial_data[data_column])

            # increment the running sum of total by the number of holdings by the current price of holding
            total_holdings += h[1] * curr_price

        return total_holdings + balance # total assets is the sum of holdings and balance
    
    def calculate_daily_gain_loss(self):
        '''
        Calculate the daily gain/loss based from open-close (daily gain/loss = (close - open) / open)
        '''

        day_open = self.total_daily_assets_open
        day_close = self.total_daily_assets_close

        # Calculate the daily gain/loss for each day
        for i in range(len(self.total_daily_assets_open)):
            self.daily_gain_loss[i] = (day_close[i] - day_open[i]) / day_open[i]

        return True

    def calculate_monthly_gain_loss(self):
        '''
        Calculate the monthly gain/loss based from open-close

        Maybe month to date?
        '''
        self.monthly_gain_loss['dates'].append(self.dates[0])
        self.monthly_gain_loss['gain_loss'].append(0)
        
        curr_data = self.total_daily_assets_open[0]
        prev_data = self.total_daily_assets_open[0]

        for i in range(len(self.dates)):
            # If first of month
            if self.dates[i].day == 1:
                curr_data = self.total_daily_assets_open[i]
                self.monthly_gain_loss['dates'].append(self.dates[i])
                self.monthly_gain_loss['gain_loss'].append((curr_data - prev_data) / prev_data)
                prev_data = curr_data
                
        return
        
    def calculate_win_rate(self):
        '''
        Calculate and store count for total actions, winning actions, and win rate
        '''

        total_action_count = 0 # Variable that keeps track of total actions undertaken by strategy
        winning_action_count = 0 # Variables that keeps track of winning actions undertaken by strategy
        
        transactions = self.portfolio.transactions

        for t in transactions:
            # Only 'sell' transactions can be considered for win/loss
            if t[0] == 'sell': 
                total_action_count += 1

                # Check if transaction is profitable
                if t[4] > 0:
                    winning_action_count += 1
        
        self.total_action = total_action_count # Update the total_action parameter in strategy
        self.winnning_action = winning_action_count # update the wining_action parameter in strategy

        self.win_rate = winning_action_count / total_action_count # Update the win_rate parameter in strategy

        return True

    def calculate_sharpe_ratio(self) :
        #E[Returns - Riskfree Returns]/standard deviation of excess return
        #Benchmark/RiskReturns S&P
        if len(self.daily_gain_loss)==0:
            raise ValueError("Empty data for daily gain/loss")

        assert len(self.daily_gain_loss)==len(self.benchmark()), "Number of benchmark values does not match number of values in daily gain/loss."
        return_differentials = [returns - riskfree for returns, riskfree in zip(self.daily_gain_loss, self.benchmark())]
        return_differentials = np.array(return_differentials)
        expected_differential = np.mean(return_differentials)
        std = np.std(np.array(self.daily_gain_loss))
        assert std!=0, "Standard deviation is 0. Cannot compute ratio."
        self.sharpe_ratio = expected_differential/std
        return True

    def is_trading_date(self, date):
        '''
        Verify if the given date is a trading day, return boolean
        Should only be called by back_testing()
        
        date: datetime object
        '''
        return not date in self.nyse_holidays # checking if date exists in holiday dict
    
    def next_nearest_trading_date(self, date):
        '''
        Return the next nearest trading date as a datetime object
        Should only be called by back_testing()
        
        date: datetime object
        '''
        while not self.is_trading_date(date): # check if current date is trading date
            date+= timedelta(days=1) # move onto next date
        
        return date
    
    def handle_run_daily(self):
        '''
        handler for run_daily, to be called in back_testing()
        '''
        self.on_market_open()
        self.run_daily()
        self.on_market_close()
    

    def place_order(self, stock_name, shares):
        '''
        handler for buy/sell, set shares > 0 for buy and < 0 for sell
        this function should be called by users in the followed functions only

        stock_name: string
        shares: float
        '''
        stock_price = self.data['date'==self.current_date & 'Name'==stock_name]
        if self.current_time: 
            stock_price = stock_price['open']
        else:
            stock_price = stock_price['close']
        self.portfolio.place_order(stock_name, stock_price, shares)

        
    ################################################################################
    # below are methods that the designer of strategy should override
    # developlers shouldn't modified anything below this line
    ################################################################################
    '''
    Important Note to Users:

                    Since we only have open/close data at the moment, 
                    we can only place at-the-open/at-the-close orders.
                    Users should place the orders in the corresponding
                    functions below.

    '''
    ################################################################################


    def on_market_close(self):
        '''
        This method should be overided by the designer of strategy on an instance level
        with python's type package
        Should be executed before market close everyday
        '''
        # should be used for placing at-the-close orders and stock selection
        pass

    def on_market_open(self):
        '''
        This method should be overided by the designer of strategy on an instance level
        with python's type package
        Should be executed before market open every virtual day
        '''
        # should be used for placing at-the-close orders and stock selection
        pass
    
    def run_daily(self):
        '''
        This method should be overided by the designer of strategy on an instance level
        with python's type package
        Should be executed before market open every virtual day
        '''
        pass
    
    def run_weekly(self):
        '''
        This method should be overided by the designer of strategy on an instance level
        with python's type package
        Should be executed before market open every virtual week on the day specified (or Mon as default)
        If date specified is not a trading date, then find the next nearest trading date
        '''
        pass
        
    def run_monthly(self):
        '''
        This method should be overided by the designer of strategy on an instance level
        with python's type package
        Should be executed before market open every virtual month on the day specified (or 1st as default)
        If date specified is not a trading date, then find the next nearest trading date
        '''
        pass
