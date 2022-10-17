# Execution Platform Guidelines
CCXT Documentation can be found here: [CCXT Documentation](https://docs.ccxt.com/en/latest/)
## We will be using CCXT (CryptoCurrency eXchange Trading Library) to perform all necessary market orders and to query all relevant account details.
### Goals
1. Write an API wrapper (a big class with a ton of methods) to perform all market orders and to retrieve all relevant data related to these orders and accounts.
2. Develop built-in data management in order to log every action (including API failures)
   * Log all API calls with timestamps and relevant info. (CCXT might be able to do this for us)
   * Format the data into CSVs (pandas)
   * Need to work with the data management team in order to route logging
4. Make sure orders interops with the queue properly if an order fails (Guessing we need to build another queue with all failed orders)

### Steps
1. Include functions for every interaction listed under the Private API section in the CCXT documentation 
    - manage personal account info
    - query account balances
    - trade by making market and limit orders
    - create deposit addresses and fund accounts
    - request withdrawal of fiat and crypto funds
    - query personal open / closed orders
    - query positions in margin/leverage trading
    - get ledger history
    - transfer funds between accounts
   
**Some of the necessary functions**
- fetchBalance (): Fetch Balance.
- createOrder (symbol, type, side, amount[, price[, params]])
- createLimitBuyOrder (symbol, amount, price[, params])
- createLimitSellOrder (symbol, amount, price[, params])
- createMarketBuyOrder (symbol, amount[, params])
- createMarketSellOrder (symbol, amount[, params])
- cancelOrder (id[, symbol[, params]])
- fetchOrder (id[, symbol[, params]])
- fetchOrders ([symbol[, since[, limit[, params]]]])
- fetchOpenOrders ([symbol[, since, limit, params]]]])
- fetchCanceledOrders ([symbol[, since[, limit[, params]]]])
- fetchClosedOrders ([symbol[, since[, limit[, params]]]])
- fetchMyTrades ([symbol[, since[, limit[, params]]]])
- editOrder (id, symbol, type, side, amount, price = undefined, params = {})
- cancelOrder (id, symbol = undefined, params = {})

### Best Practices
1. Write documentation!!!
    * Include this before every function: """*description of what function does*"""
2. Create unit tests to ensure all functions are working properly
    * 50% of test cases must pass before being pushed to the **dev** branch
    * 80% of test cases must pass before being pushed to the **test** branch
    * Code reviews before pushing to the **main**/**prod** branch
