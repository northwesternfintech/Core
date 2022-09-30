# Data Acquisition Guidelines
Websocket Documentation can be found here: [Websocket Documentation](https://websockets.readthedocs.io/en/stable/)
Coinbase Documentation can be found here: [Coinbase Websocket Documentation](https://docs.cloud.coinbase.com/prime/docs/websocket-feed)
Kucoin Documentation can be found here: [Kucoin Websocket Documentation](https://docs.kucoin.com/#apply-connect-token)
## We will be using websocket to scrape real-time market level 1 and level 2 data
### Goals
1. Query one websocket(for now, just Coinbase)
2. Build an AWS wrapper that saves data to the cloud
3. Develop a short API algo that runs every websocket fails (collaborate with execution platform team).
4. Universalize a file naming convention and paradigm to save data
5. Use queues to get data to main_script
6. Add redundancy through multiple sockets
7. Store data locally and archive to AWS3 Glacier

### Steps
1. Build one websocket exchange entirely (Coinbase)
    * Each websocket should ONLY take two multiprocessing queues (one for each level of market data), and a list of coins (str).
    * Each websocket should be a class with member functions that 
    * Scraped data should be outputted into each respective queue (i.e. queue_1, queue_2)
2. Implement multiple websockets following the same format
3. Combine all the websockets to be called within a main_script file which cycles through broken/working websockets and contains the two queues which will be inputted into every websocket initialization
5. 
### Best Practices
1. Write documentation!!!
    * Include this before every function: """*description of what function does*"""
2. Create unit tests that ensure 3 goals:
    * each websocket receives data each tick
    * the main_script is able to 
    * data is able to stored locally and to AWS
2. Create unit tests to ensure all functions are working properly

3. 
    * 50% of test cases must pass before being pushed to the **dev** branch
    * 80% of test cases must pass before being pushed to the **main** branch

