# Core

https://docs.google.com/document/d/1y9kN33lvFZXuBcid_EwmNprfRi7zRq4vD1NgKDrtXcU/edit?usp=sharing

Goal: Finish the quant firm (Python)

Operating Market: Crypto

Required Deliverables:
Data Acquisition - David
Keep it to one exchange, build the entire thing, verify it works, and then move on.
Implement a redundancy system to halt execution if websocket fails, and use a failsafe api calling loss reducer in its place. 
Unit Testing: Ensure each part of data flow gets data
Websocket -> receives data each tick
Engine -> gets data out of queue properly
Store data -> ensure data gets to aws/hdd

 Query Websocket - Coinbase
 Building Boto3/AWS Wrapper
 Design simple API algo that runs when websocket fails (use execution platform)
 Develop data paradigm
 Get data to main script using queue lol
 Add redundancy through further sockets
 Store data locally, archive to S3 Glacier 

Execution Platform - Rich
Call CCXT to perform our orders. 
We need redundancy here too. Log API failures. 
Testing Methodology: Make sure functions actually query, return as expected. 

Wrap the API
Write documentation
Build in data management
Build redundancy
If an order fails, make sure it interops with the order queue properly. 
Implement logging
Work w/ Info Control to route logging










Information Control - Jason 
Keep track of trades, balances, and holdings. IMPORTANT: do this through the api response calls, to ensure that inter-language data management is not required.

Build in data storage and variables w/ local storage as well.
Analyze and store server health data vs. time.
Generate time series data about server health metrics
Analyze and store Jenkins time series as well. 
Build structures to route data through the system. 
Network w/ Data Sockets team to move data through mp queue.
Work with Execution Platform to get data logged
Work with Backtesters to store and move logs. 

Backtesting - Gary
Begin by using Alpaca Paper API to backtest. 
Build in a post-backtest summary data page, including graphs, to understand performance. Log files. 
Use alpaca if time requires, but do 2) if time permits. 
Build functioning backtester
Figure out data - historical 
Query data and store it
Run it against time which each tick
Return result after all ticks
Networking -> Find the algorithm it is called with
Develop the log file
Develop visualizations
Make sure it is easy to use and well documented. 

Algorithm Interop - Squad
Use hooks to allow Desk Programs to interface with the backtest and execution environments. 
PLEASE MANUALLY CR ALGORITHMS!!!! WRITE TYPE TESTS! Failures of functioning algorithms when integrated is NOT THE RESPONSIBILITY OF THE DESK. 
Build out the engine/central file in its functionality.
For each algorithm:
CR the algorithm
“Find” the algorithms
Hook onto relevant methods and fields
Build unit tests surrounding each algorithm
Write and work on integration and integration tests
Maintain pipeline and devops

Stretch Goals:
CCXT Pro Added
This will be available at some point during Q3 FY22. 
Recommending moving from individual sockets to CCXT as soon as possible. 
Low Level Conversion
Pending Ethan<>Mitchell Deliberation, begin converting platform to C++. Same rules remain.

Testing guidelines:
UNIT TESTS REQUIRED.
50% COVERAGE REQUIRED FOR MERGE ON DEV, 80% BEFORE MERGE TO PROD

Ideal Timeline:
Week 2 of October: All Dev Lines done
Week 3: All Prod Lines done
Week 4: All integration done, fire it up
Week 1 of November: All strats backtested

