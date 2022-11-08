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
1. Include functions for interactions listed under the Unified/Private API section in the CCXT documentation:

   
**FUNCTIONS NEEDED**
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
- fetchStatus ([, params = {}])

2. Need to find a way to log every action made with a time stamp and any relevant info. This will be sent to the Data Framework team.
- Just convert the inputs into a csv. return this data
- if any api call fails, need to make sure the order gets put back into the order queue correctly

3. Create an order queue? to save all performed orders in the order they were submitted.

### Best Practices
1. Write documentation!!!
    * Include this before every function: """*description of what function does*"""
2. Create unit tests to ensure all functions are working properly
    * 50% of test cases must pass before being pushed to the **dev** branch
    * 80% of test cases must pass before being pushed to the **test** branch
    * Code reviews before pushing to the **main**/**prod** branch