# Execution Platform Guidelines
CCXT Documentation can be found here: [CCXT Documentation](https://docs.ccxt.com/en/latest/)
## We will be using CCXT (CryptoCurrency eXchange Trading Library) to perform and log all market orders
### Goals
1. Write an API wrapper to perform all market orders and to retrieve all relevant data related to these orders and accounts.
2. Develop built-in data management in order to log every action (including API failures)
   * Will probably format data into CSVs with Pandas
   * These logs will be used by the Data Control team
4. Make sure orders interops with the queue properly if an order fails

### Steps
1. Include functions for every interaction listed under the Private API section in the CCXT documentation
    * manage personal account info
    * query account balances
    * trade by making market and limit orders
    * create deposit addresses and fund accounts
    * request withdrawal of fiat and crypto funds
    * query personal open / closed orders
    * query positions in margin/leverage trading
    * get ledger history
    * transfer funds between accounts
    * use merchant services

2. Include functions for every interaction listed under the Public API section in the CCXT documentation
    * instruments/trading pairs
    * price feeds (exchange rates)
    * order books (L1, L2, L3…)
    * trade history (closed orders, transactions, executions)
    * tickers (spot / 24h price)
    * OHLCV series for charting
### Best Practices
1. Write documentation!!!
    * Include this before every function: """*description of what function does*"""
2. Create unit tests to ensure all functions are working properly
3. 50% code coverage before being pushed to the dev branch
80% of code coverage before being pushed to the test branch
100% unit coverage + integration tests verified before pushing to the main branch
    * 50% of test cases must pass before being pushed to the **dev** branch
    * 80% of test cases must pass before being pushed to the **test** branch
    * 100% unit coverage + integration tests verified before pushing to the **main** branch
