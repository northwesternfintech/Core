# Execution Platform Guidelines
CCXT Documentation can be found here: [CCXT Documentation](https://docs.ccxt.com/en/latest/)
## We will be using CCXT (CryptoCurrency eXchange Trading Library) to perform and log all market orders
### Goals
1. Write an API wrapper to simplify the process of making market orders
2. Develop built-in data management in order to log every action (including API failures)
   * Will probably format data into CSVs with Pandas
   * These logs will be used by the Data Control team
4. Make sure orders interops with the queue properly if an order fails

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
