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


# Build Coinbase Websocket Class 
class CoinbaseWebSocket(WebSocket):
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
        super().__init__(queue_1, queue_2, coins)
        self.channels = ['ticker', 'level2']
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
    
    async def async_run(self):  # Full Asynchronous Run 
        try:
            async with websockets.connect('wss://ws-feed.exchange.coinbase.com', max_size = 1_000_000_000) as websocket:
                await websocket.send(json.dumps(self.sub_message))
                while True:
                    message = await websocket.recv()
                    temp_json = json.loads(message)
                    # Organizing Data for pandas DataFrame
                    msg_data = []
                    time_id = []
                    curr_dt = None 
                    if temp_json['type'] == 'ticker':
                        curr_dt = temp_json['time'].replace('Z', '')
                        curr_dt = curr_dt.replace('T', ' ')
                        msg_data = {
                            'exchange': 'coinbase',
                            'ticker': temp_json['product_id'],
                            'price': temp_json['price']
                        }
                        time_id = [curr_dt]
                        if self.queue_1.full():
                            print('working 1')
                        if msg_data != [] and time_id != []:
                            df = pd.DataFrame(data=msg_data, index=time_id)
                            # print(df)
                            self.queue_1.put(df) 
                    # If market 2 data
                    elif temp_json['type'] == 'l2update':
                        curr_dt = temp_json['time'].replace('Z', '')
                        curr_dt = curr_dt.replace('T', ' ')
                        for update in enumerate(temp_json['changes']):
                            msg_data = {
                                    'exchange': 'coinbase',
                                    'ticker': temp_json['product_id'],
                                    'side': update[0],
                                    'price': update[1],
                                    'quantity': update[2]
                                }
                            time_id = [curr_dt]
                            if self.queue_2.full():
                                print('working 2')
                            if msg_data != [] and time_id != []:
                                df = pd.DataFrame(data=msg_data, index=time_id)
                                print(df)
                                self.queue_2.put(df) 
        except Exception:
            print(traceback.format_exc())
        

# Async Script Start
async def main(coins): 
    q = multiprocessing.Queue()
    r = multiprocessing.Queue()
    cwr = CoinbaseWebSocket(q, r, coins)
    await cwr.async_run()  # TODO: Don't access private methods

q = multiprocessing.Queue()
r = multiprocessing.Queue()
coins = ['BTC-USDT', 'ETH-USDT']
cwr = CoinbaseWebSocket(q, r,coins)
cwr.run()
