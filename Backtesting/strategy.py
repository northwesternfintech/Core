import engine
import matplotlib
import pandas as pd
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
        self.portfolio = portfolio(starting_balance = start_balance, 
                                   transaction_cost = transaction_cost)
    
    def back_testing(self, start_time=None, end_time=None):
        '''
        back_testing takes in the start and end time, then proceed to 
        test the performance of the strategy
        
        start_time, end_time: strings in the format of "yyyy-mm-dd"
        '''
        start = start_time or '2013-03-28'
        end = end_time or '2018-02-05'

        current_time = datetime.strptime(start, "%Y-%m-%d").date()
        end_time = datetime.strptime(end, "%Y-%m-%d").date()
        
        print('\n started backtesting')
        while current_time != end_time:
            pass
        print('finished backtesting, started visualizing')
        
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
    
    def visualize(self): 
        '''
        This function should be executed after backtesting for visualizing the 
        performance of the strategy
        Use matplotlibe/seaborn/etc. to make graphs, then display the logs by the 
        side, gotta make this look fancy
        '''
        pass

    def is_trading_date(self, date):
        '''
        Verify if the given date is a trading day, return boolean
        Should only be called by back_testing()
        
        date: datetime object
        '''
        pass
    
    def next_nearest_trading_date(self, date):
        '''
        Return the next nearest trading date as a datetime object
        Should only be called by back_testing()
        
        date: datetime object
        '''
        pass
    
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
        
    ################################################################################
    # below are methods that the designer of strategy should override
    # developlers shouldn't modified anything below this line
    ################################################################################
    
    def on_market_close(self):
        '''
        This method should be overided by the designer of strategy on an instance level
        with python's type package
        Should be executed before market close everyday
        '''
        # it's mainly used for placing at-the-close orders and stock selection
        # but at the moment, the resolution of data we have don't allow us to perform any
        # at-the-close orders :(
        pass

    def on_market_open(self):
        '''
        This method should be overided by the designer of strategy on an instance level
        with python's type package
        Should be executed before market open every virtual day
        '''
        # due to resolution of data
        # its functionality is pretty much the same as on_market_close()
        pass
    
    def run_daily(self):
        '''
        This method should be overided by the designer of strategy on an instance level
        with python's type package
        Should be executed before market open every virtual day
        '''
    
    def run_weekly(self):
        '''
        This method should be overided by the designer of strategy on an instance level
        with python's type package
        Should be executed before market open every virtual week on the day specified (or Mon as default)
        If date specified is not a trading date, then find the next nearest trading date
        '''
        
    def run_monthly(self):
        '''
        This method should be overided by the designer of strategy on an instance level
        with python's type package
        Should be executed before market open every virtual month on the day specified (or 1st as default)
        If date specified is not a trading date, then find the next nearest trading date
        '''
