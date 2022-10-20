'''
This is the base Websocket class that you will need to inherit across every websocket.
 
In your subclasses, you should override the __init__ method so you can store info that you might need
store across sub-class methods, such as channels you need to subscribe to, subscription messages, etc.

The main_script will create each websocket with the following inputs:
queue_1 -> stores the multiprocessing queue that stores market level 1 data (see Coinbase_Websocket.py)
queue_2 -> stores the multiprocessing queue that stores market level 2 data (ditto)
coins -> stores strings that each represent crypto tickers 
'''

class Websocket:
    def __init__(self, queue_1, queue_2, coins = []):
        self.queue_1 = queue_1
        self.queue_2 = queue_2
        self.coins = coins

    