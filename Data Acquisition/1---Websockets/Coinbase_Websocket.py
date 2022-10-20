import asyncio
import websockets
import requests
import multiprocessing
import time
import json
import pandas as pd
import traceback
from time import time
from datetime import datetime 
from scipy.fft import idst 
from uuid import uuid4

#https://docs.cloud.coinbase.com/exchange/docs/websocket-channels
#Creating Coinbase Websocket Class 
class Coinbase_Websocket():
    #Passing queue and other relevant information
    def __init__(self, queue_1, queue_2, coins = []):
        self.queue_1 = queue_1
        self.queue_2 = queue_2
        self.coins = coins
        self.channels = ['ticker', 'level2']
        self.sub_message = self.on_open()
   
    def on_open(self): # Generates a subscribe message to be converted into json to be sent to endpoint
        subscribe_message = {}
        subscribe_message["type"] = "subscribe"
        subscribe_message["product_ids"] = self.coins
        subscribe_message["channels"] = self.channels
        return subscribe_message
    
    async def run(self): #Full Asynchronous Run 
        try:
            async with websockets.connect('wss://ws-feed.exchange.coinbase.com', max_size = 1_000_000_000) as websocket:
                await websocket.send(json.dumps(self.sub_message))
                while True:
                    message = await websocket.recv()
                    # print(message)
                    temp_json = json.loads(message)
                    #Setting Variables for Data Frame 
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
                            df = pd.DataFrame(data = msg_data, index = time_id)
                            print(df)
                            self.queue_1.put(df) 
                    elif temp_json['type'] == 'l2update':
                        curr_dt = temp_json['time'].replace('Z', '')
                        curr_dt = curr_dt.replace('T', ' ')
                        msg_data = {
                                'exchange': 'coinbase',
                                'ticker': temp_json['product_id'],
                                'side': temp_json['changes'][0][0],
                                'price': temp_json['changes'][0][1],
                                'quantity': temp_json['changes'][0][2]
                            }
                        time_id = [curr_dt]
                        if self.queue_2.full():
                            print('working 2')
                        if msg_data != [] and time_id != []:
                            df = pd.DataFrame(data = msg_data, index = time_id)
                            print(df)
                            self.queue_2.put(df) 


        except Exception:
            import traceback
            print(traceback.format_exc())

    async def _main(self):
        await self.run()

    def _run_(self):
        asyncio.run(self._main())
        

    #goal is to get the DateTime from the Json and store into tickers 
    #then put into database 
#Async Script Start
async def main(coins): 
    q = multiprocessing.Queue()
    r = multiprocessing.Queue()
    cwr = Coinbase_Websocket(q, r, coins)
    await cwr.run()

# q = multiprocessing.Queue()
# r = multiprocessing.Queue()
# coins = ['BTC-USDT', 'ETH-USDT']
# cwr = Coinbase_Websocket(q, r,coins)
# cwr._run_()