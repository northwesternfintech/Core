# Data Acquisition Guidelines
# Documentation Compilation
## Central Script
[Websocket Documentation](https://websockets.readthedocs.io/en/stable/)

[Coinbase Websocket Documentation](https://docs.cloud.coinbase.com/prime/docs/websocket-feed)

[Kucoin Websocket Documentation](https://docs.kucoin.com/#apply-connect-token)

### Python CLI
[Pandas Documentation](https://pandas.pydata.org/docs/)
### APIS
[Coinbase Documentation](https://www.coinapi.io/)
## Youtube Videos for Easier Understanding
[Basic Binance Websocket Tutorial](https://youtu.be/z2ePTq-KTzQ)

[Multiprocessing Tutorial: Watch Up to Video 31](https://youtu.be/Lu5LrKh1Zno)

[Async Tutorial](https://youtu.be/6RbJYN7SoRs)

# Goals
The data acquisition team's ultimate goal is to independently store real-time market level 1 and level 2 market data. If you've every used packages like yfinance, we are essentially implementing those packages but in crypto, with the advantage of being able to gain 1) real-time data, 2) bypassing API limits that restrict the rate of data acquisition 3) data convention interoperability (we can change our data formatting however we see fit). 

Once we have one websocket working, we will create multiple (ideally around 5 total) to ensure data output stability via redundancy. To account for the case in which all data sockets fail, we will also create a small algorithm that queries data from a pre-made API (likely CoinAPI!) that works around API limits as much as possible to ensure some level of data output (will likely be in deliberation with other teams).

We want to be able to take this data, universalize its formatting (probably .csv or .json), store it locally to servers. Then, our other teams will use our data how they see fit, and we can update our data convention based on their feedback.

# Broad Steps
1. Query one websocket (for now, just Coinbase)
2. Develop a short API algo that runs every websocket fails (collaborate with execution platform team).
3. Universalize a file naming convention and paradigm to save data.
4. Use queues to get data to a main_script.py which uses multiprocessing to sequence which websockets to scrape data from based on whether each websocket is dead or not.
5. Add redundancy by creating multiple sockets.
6. Store data locally and archive to AWS3 Glacier.

### Initial Steps
1. Build one websocket exchange entirely (Coinbase)
    * Each websocket should ONLY take two multiprocessing queues (one for each level of market data), and a list of coins (for each ticker we want to scrape data from.
    * Each websocket should be a class with member functions call each other to culminate in a function called  "Coinbase_Websocket.run" and have the queue stored within the class fill up with formatted data!
    * Scraped data should be outputted into each respective queue (i.e. queue_1, queue_2)
2. Implement multiple websockets following the same format
3. Combine all the websockets to be called within a main_script file which cycles through broken/working websockets and contains the two queues which will be inputted into every websocket initialization

### Beneficial Practices
1. Write documentation!!!
    * Include this before every function: """*description of what function does*"""
    * Don't make it too long though; Ethan will slaughter me
2. Create unit tests that ensure the following goals:
    * each websocket receives data each tick
    * the queue successfully outputs data in the correct sequence
    * data is able to stored locally and to AWS
    * the simple API algorithm doesn't get API limited and ratio'd to the ground
    * the main_script is able to cycle through every websocket and also
3. Ask me if you have data acquisition-related ANY questions. Even the most basic clarification ones!
