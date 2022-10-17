# Data Acquisition Guidelines
Websocket Documentation can be found here: [Websocket Documentation](https://websockets.readthedocs.io/en/stable/)
Coinbase Documentation can be found here: [Coinbase Websocket Documentation](https://docs.cloud.coinbase.com/prime/docs/websocket-feed)
Kucoin Documentation can be found here: [Kucoin Websocket Documentation](https://docs.kucoin.com/#apply-connect-token)
### Youtube Videos for Greater Understanding
# Basic Binance Websocket Tutorial:
https://youtu.be/z2ePTq-KTzQ
# Multiprocessing Tutorial: Watch Up to Video 31
https://youtu.be/Lu5LrKh1Zno
### Goals
The data acquisition team's ultimate goal is to independently store real-time market level 1 and level 2 market data. If you've every used packages like yfinance to do basic data analysis on past stock data within set periods, we are essentially implementing those packages, with the advantage of being able to gain 1) real-time data, 2) bypassing API limits that restrict the rate of data acquisition 3) data convention interoperability (we can change our data formatting at any time). 

### Broad Steps
To achieve the above goal, we will create a Python class called Websocket, which takes in the parameters 
1. Query one websocket (for now, just Coinbase)
2. Build an AWS wrapper that saves data to the cloud
3. Develop a short API algo that runs every websocket fails (collaborate with execution platform team).
4. Universalize a file naming convention and paradigm to save data.
5. Use queues to get data to a main_script.py which uses multiprocessing to 
6. Add redundancy by creating multiple sockets
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

