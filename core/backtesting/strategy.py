import matplotlib
import pandas as pd
import holidays
import datetime
import portfolio

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

        # list of total assets in a given day at open/open
        # index maps to index of self.dates
        self.total_daily_assets_open = [] 
        self.total_daily_assets_close = []

        self.daily_gain_loss = [] # List of daily gain/loss indexed to self.dates

        self.dates = [] # list of dates / index maps to index of self.total_daily_assets

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
        
        print('\n started backtesting')
        while self.current_time != end_time:
            pass

            # Run daily/weekly/monthly
            
            # append total amount of assets to self.total_daily_assets_open
            # append total amount of assets to self.total_daily_assets_close

            
            # Increment self.curr_time
            
        # Calculate statistical data

        print('\n finished backtesting, started visualizing')
        
        self.visualize()
    
    def log(self, msg, time): 
        '''
        This function logs every action that the strategy has taken, from
        stock selection to buying/selling a stock
        The logs should be display alongside the curves and visualizing
        
        msg: a string that describes the action to be logged
        time: the time that the action took place
        '''
        self.log.append([msg, time])
    
    def visualize(self, plot_total_assets=True, plot_daily_returns=True, plot_win_rate=True): 
        '''
        This function should be executed after backtesting for visualizing the 
        performance of the strategy
        Use matplotlibe/seaborn/etc. to make graphs, then display the logs by the 
        side, gotta make this look fancy

        Boolean parameters gives user control over which variables to display
        '''

        if(plot_total_assets):
            # plot self.total_daily_assets vs self.dates with plt
            pass
        if(plot_daily_returns):
            # plot self.daily_gain_loss vs self.dates with plt
            pass

        # ...

        pass

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

    def get_win_rate(self): return [self.win_rate, self.winning_action, self.total_action]

    def calculate_total_assets(self, data_column='open'):
        '''
        calculate the total amount of assets in a portfolio at the selected time each
        day.

        Should be run during backtesting for each iteration.
        '''
        total_output = 0
        balance = self.portfolio.get_balance()
        holdings = self.portfolio.get_holdings()
        data = self.data

        for h in holdings:
            str_date = self.current_time.strf("%Y-%m-%d")
            partial_data = data[data['Name']==h[0] and data['date']==str_date]
            price = float(partial_data[data_column])
            total_output += h[1] * price

        return total_output + balance
    
    def calculate_daily_gain_loss(self):
        '''
        Calculate the daily gain/loss based from open-close
        '''

        for i in range(len(self.total_daily_assets_open)):

            day_open = self.total_daily_assets_open[i]
            day_close = self.total_daily_assets_close[i]

            self.daily_gain_loss[i] = (day_close - day_open) / day_open

        return

    def calculate_win_rate(self):
        '''
        Calculate and store count for total actions, winning actions, and win rate
        '''

        total_action_count = 0
        winning_action_count = 0
        
        transactions = self.portfolio.transactions
        for t in transactions:
            if t[0] == 'sell':
                total_action_count += 1
                if t[4] > 0:
                    winning_action_count += 1
        
        self.total_action = total_action_count
        self.winnning_action = winning_action_count

        self.win_rate = winning_action_count / total_action_count

        return


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
            date+= datetime.timedelta(days=1) # move onto next date
        
        return date
    
    def handle_run_daily(self):
        '''
        handler for run_daily, to be called in back_testing()
        '''
        pass
    
    def handle_run_weekly(self):
        '''
        handler for run_weekly, to be called in back_testing()
        '''
        pass
    
    def handle_run_monthly(self):
        '''
        handler for run_monthly, to be called in back_testing()
        '''
        pass

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
