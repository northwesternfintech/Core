import asyncio
import json
import multiprocessing
import time
import traceback
from datetime import datetime
from time import time
from uuid import uuid4

import pandas as pd
import requests
import websockets
from scipy.fft import idst

from web_socket import WebSocket

import gemini
r = gemini.PrivateClient("EXAMPLE_PUBLIC_KEY", "EXAMPLE_PRIVATE_KEY")
# Alternatively, for a sandbox environment, set sandbox=True
r = gemini.PrivateClient("EXAMPLE_PUBLIC_KEY", "EXAMPLE_PRIVATE_KEY", sandbox=True)

# Build Gemini Websocket Class 
class GeminiWebSocket(WebSocket):
    def __init__(self, queue_1, queue_2, coins):
        """Passing queue_1, queue_2, coins, setting subscription message and channels to subscribe to
        Parameters
        ----------
        queue_1 : _type_
            _description_
        queue_2 : _type_
            _description_
        coins : _type_
            _description_
        """        
        super().__init__(self, queue_1, queue_2, coins)
        

        self.channels = ['level1', 'level2']

        self.queue_1 = pd.DataFrame(columnns = ["bid", "bid_size", "ask", "ask_size"])
        self.queue_2 = pd.DataFrame(columns=["price", "amount", "side"])
        self.sub_message = self.on_open()
   
    def on_open(self):
        """Generates a subscribe message to be converted into json to be sent to endpoint
        Returns
        -------
        _type_
            _description_
        """        
        subscribe_message = {
            "type": "subscribe",
            "product_ids": self.coins,
            "channels": self.channels
        }
        return subscribe_message
    
    async def _run(self):  # Full Asynchronous Run 
        try:
            async with websockets.connect('wss://api.gemini.com/v1/marketdata/{}'.format(symbol)) as websocket:
                #updates for a specific symbol
                await websocket.send(json.dumps(self.sub_message).format(symbol))
                while True:
                    message = await websocket.recv()
                    temp_json = json.loads(message)

                    #level 1 data
                    if temp_json["channel"] == "level1":
                        bid = data["bid"]
                        bid_size = data["bid_size"]
                        ask = data["ask"]
                        ask_size = data["ask_size"]
                        self.queue_1.loc[len(level1_data)] = [bid, bid_size, ask, ask_size]
                        
                        if self.queue_1.full():
                                print('working 1')

                    # If market 2 data
                    elif temp_json["channel"] == "level2":
                        
                        price = data["price"]
                        amount = data["amount"]
                        side = data["side"]
                        
                        self.queue_2.loc[len(level2_data)] = [price, amount, side]

                        if self.queue_2.full():
                            print('working 2')

        except Exception:
            print(traceback.format_exc())
        

# Async Script Start
async def main(coins): 
    q = multiprocessing.Queue()
    r = multiprocessing.Queue()
    cwr = GeminiWaseWebSocket(q, r, coins)
    await cwr._run()  # TODO: Don't access private methods

q = multiprocessing.Queue()
r = multiprocessing.Queue()
coins = ['BTC-USDT', 'ETH-USDT']
cwr = GeminibaseWebSocket(q, r,coins)
cwr.run()