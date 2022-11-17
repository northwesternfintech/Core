# Introduction

A backtester provides a set of tools for estimating the future performance of a strategy for the user by testing the strategy against historical price data and presenting its performance statistics both graphically and numerically.

# How to Use: 

Users should first initialize the instance when they want to use it, and then they will have to overwrite some functions of the instance to implement a strategy (see more details below), and then they would be able to see the performance of the strategy by running the backtesting function with a time interval input. 

    Step 1: Create instance

            my_strategy = Strategy(transaction_cost=0.0065, start_balance=10000, week_day=1, month_day=1)

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

