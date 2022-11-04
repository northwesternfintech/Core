'''
This is the base Websocket class that you will need to inherit across every websocket.
 
In your subclasses, you should override the __init__ method so you can store info that you might need
store across sub-class methods, such as channels you need to subscribe to, subscription messages, etc.

The main_script will create each websocket with the following inputs:
queue_1 -> stores the multiprocessing queue that stores market level 1 data (see Coinbase_Websocket.py)
queue_2 -> stores the multiprocessing queue that stores market level 2 data (ditto)
coins -> stores strings that each represent crypto tickers 
'''
from abc import ABC, abstractmethod
from typing import Dict

import asyncio


class WebSocket(ABC): # TODO: Decide whether its "websocket" or "web socket"
    def __init__(self, queue_1, queue_2, coins=[]):  # TODO: Add more descriptive queue names
        self.queue_1 = queue_1
        self.queue_2 = queue_2
        self.coins = coins

    @abstractmethod
    def on_open(self) -> Dict:
        """Generates a subscribe message to be converted into json to be sent 
        to endpoint

        Returns
        -------
        Dict
            Subscribe message to be sent to endpoint
        """
        raise NotImplementedError

    @abstractmethod
    async def async_run(self) -> None:
        """
        Add all your async run junk here
        """
        raise NotImplementedError

    async def main(self):  # TODO: Not sure if this is needed add docstring for purpose
        await self.async_run()

    def run(self):  # TODO: Add docstring for purpose
        asyncio.run(self.main())
