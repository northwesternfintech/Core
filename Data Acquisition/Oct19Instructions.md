# Data Acquisition Week 1
## Project Description:
Create 4 Websockets from scratch, the simple API algo, and a simple queue tester. Coinbase should be functional, so those building websockets this week should look to that document for sub-class method-writing reference. 

## Ideal Deadline: Oct 26

## Assignments:
Ariana - Binance_Websocket.py
Brennan - AWS3 Wrapper thing
Louis - Simple API Algo that queries queries data from CoinAPI
Lucy - Gemini_Websocket.py
Sam - Kucoin_Websocket.py
Yetayal - Kraken Websocket.py
Jay - Write a main_script that initializes the multiprocessing queues and every websocket within a main function, then uses a process executing pool that 

## Websocket Steps:
1. Create initialization method that uses the parent class Websocket_Class to store queue_1, queue_2, and coins.
2. Write wrapper functions that allow you to write the requisite private wrapper functions to request subscribe each websocket's ideal subscription methods (I would recommend that you subscribe to a market level 1 channel first)
3. Create the asynchronous run function and confirm that the JSON subscription outputs into queue_1.
4. Test the websocket with a simple case and a print statement (see Coinbase).
5. Write #1: ._main_ and #2: ._run_ methods that #1: await for the run and then #2: run it via asyncio.
6. Organize the market level 1 data into a singular pandas dataFrame (see Coinbase).
7. Subscribe to market level 2 data and format it the same way as Coinbase does.

## Simple Algo API Steps:
Just write out the CoinAPI wrappers
## Documentation:
All documentation is in the Broad Websocket Instructions folder. Dependencies you might find useful have been added to each of your documents. See Coinbase_Websocket.py for the general idea of what you might want to do.

