# Introduction

A backtester provides a set of tools for estimating the future performance of a strategy for the user by testing the strategy against historical price data and presenting its performance statistics both graphically and numerically.

# How to Use: 

Users should first initialize the instance when they want to use it, and then they will have to overwrite some functions of the instance to implement a strategy (see more details below). The performance of the strategy will be available after running the backtesting function with a time interval input. See below for a more detailed procedure.

    Step 1: Create instance and load dataset

            Identify a local csv file file. You may use the data file stored in the repo if you do not have one. Then copy the absolute path of the file as an input for initializing the backtester, along with transaction cost, start balance. 

            Note: weekdays and monthdays are explained in step 2. 

            my_strategy = Strategy(transaction_cost=0.0065, start_balance=10000, week_day=1, month_day=1,
                                        data_file_path = '/someuser/documents/data.csv')

    Step 2: Implement your strategy

            Overwrite the run_daily, run_weekly, and run_monthly functions (if needed). These functions enable you to customize your strategy. The run_daily function will be       
            operated on every trading day. run_monthly will be operated on the specified month_day, and run_weekly on the specified weekday. 

            If your strategy needs to access the stock prices of the virtual day, you may access it at self.prices, which is a pandas dataframe that contains all the price data from the day. 

    Step 3: Test

            run the back_testing() function, which takes in two variables: start_time and end_time. The time inputs should be in the format of 'yyyy-mm-dd'. 
            Note: at the moment, start_time cannot be earlier than 2013-3-28, and end_time cannot be later thant 2018-2-5. 

            my_strategy.backtesting(start_time = '2013-03-28', end_time = '2018-02-05')

    Step 4: Find Output 
            
            Find your output in the local directory (same as your script). It will be stored as pictures and text files.

# Workflow

Once an instance is initialized and your strategies are implemented, a local dataframe of historical data will be loaded, and it simulates the historical trading environment in a loop that iterates through every trading day in the specified time interval. In each virtual day, buying and selling will be determined by the user specified strategies, and during the process a portfolio that contains all the virtual transactions made by the strategy will be created. After the simulation process, the backtester collects statistics (including winrate/sharpe/monthly gain/etc.) from the portfolio and present it to the users by generating both log files that sums up the performance and statistics and png files that contains the graphs.

# Functions

    Functions that the user should use:

        init() -- initialize the backtester instance, no output

                transaction_cost: float that determines the cost of every transaction
                start_balance: the balance that the strategy is starting with
                
                week_day:       every week, when it comes to the week_day specified, execute
                                the run_weekly function. Default is Monday.
                month_day:      every month, when it comes to the month_day specified, execute
                                the run_monthly function. Default is 1st.


        backtesting() -- simulate the trading environment and test the performance of the strategy.
                         This function will output graphs and logs in a local directory called 'backtester'.

                start_time:     strings in the format of "yyyy-mm-dd" for start time
                end_time:       strings in the format of "yyyy-mm-dd" for end time


        place_order() -- handler for placing orders, this function should not be called directly.
                         Instead, call this function in the run functions when you implement your strategy.

                stock_name:     string representing the name of the stock
                shares:         integer representing the number of stocks to buy/sell (negative for sell and positive for buy)

    Functions that should be overrided by the user.

        run_daily()
        run_weekly()
        run_monthly()

# Statistical Output

    Sharpe ratio: compares the return of an investment with its risk
    Winrate: how many trades your strategy wins
    Return: return of your strategy
