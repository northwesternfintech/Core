# Data Acquisition Week 1
## Project Description:
Create 4 Websockets from scratch, the simple API algo, and a simple queue tester. Coinbase should be functional, so those building websockets this week should look to that document for sub-class method-writing reference. 

## Ideal Deadline: Oct 26 (please let me know if you have no time because if so we can schedule a work day in which we get free food)

## Assignments:
Ariana - Binance_Websocket.py

Brennan - AWS3 wrapper function that saves big crypto .csv files

Louis - Simple API Algo that queries data from CoinAPI

Lucy - Gemini_Websocket.py

Sam - Kucoin_Websocket.py

Yetayal - Kraken Websocket.py

Jay - Write out main_script.py

## Websocket Steps:
1. Create initialization method that uses the parent class Websocket_Class to store queue_1, queue_2, and coins.
2. Write the requisite private wrapper functions to request subscriptions from each websocket (I would recommend that you subscribe to a market level 1 channel first).
3. Create the asynchronous run function and confirm that the JSON subscription outputs into queue_1.
4. Test the websocket with a simple case and a print statement (see Coinbase).
5. Write two asynchronous methods that basically just call run:

    A. ._main_ : awaits for the run

    B. ._run_ : runs _main_  via asyncio.

    C. ^ to be clear, the name of these are '(underscore)main(underscore)' and '(underscore)run(underscore)'.

6. Organize the market level 1 data into a singular pandas dataFrame (see Coinbase).
7. Subscribe to market level 2 data and format it the same way as Coinbase does.

## Main Script Steps:
Write out a script that initializes the multiprocessing queues and every websocket within a main function. Write out a for loop that, for every coin in a given list of coins submits the _run_ process to the executor, using an individual websocket (for now, you choose which websocket to submit _run_ via an arbitrary layered try-except that goes through and checks if _run_ is failing for every websocket). 

## CoinAPI Steps:
Just read the docs and watch the video I put in the Broad Websocket Instructions folder. The idea is that you will attempt to output very basic market data in case every websocket is failing (in this case we will probably sack the queue and directly save data from said script). Still deliberating w/ Ethan a little bit on how to get past rate limits and how exactly we want the data to be outputted, so just write the wrappers for now.

## Documentation:
All documentation is in the Broad Websocket Instructions folder. Dependencies you might find useful have been added to each of your documents. See Coinbase_Websocket.py for the general idea of what you might want to do.

