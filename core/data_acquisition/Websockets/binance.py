#Dependencies
import asyncio
import json
import multiprocessing
from datetime import datetime
from uuid import uuid4
import traceback
import regex as re

import pandas as pd
import websockets

from web_socket import WebSocket

# Build Websocket Class
class BinanceWebSocket(WebSocket):
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
        # Create list of appropriate string params for streaming
        # (e.g "btcusdt@depth@100ms" returns level 2 data for bitcoin/USDT at 100ms)
        self.params = []
        self.coin_dict = {}
        print(type(self.coins))
        for coin in self.coins:
            b_coin = re.sub(r"\W","",coin)
            self.coin_dict[b_coin] = coin
            self.params.append(b_coin.lower()+"@ticker")
            self.params.append(b_coin.lower()+"@depth@100ms")
        self.sub_message = self.on_open()

    def on_open(self):
        """Generates a subscribe message to be converted into json to be sent to endpoint

        Returns
        -------
        _type_
            _description_
        """        
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": self.params,
            "id": 1
        }
        print(subscribe_message)
        return subscribe_message

    async def async_run(self):
        try:
            async with websockets.connect('wss://stream.binance.usçç:9443/stream?', max_size = 1_000_000_000) as websocket:
                await websocket.send(json.dumps(self.sub_message))
                first = True
                while True:
                    message = await websocket.recv()
                    temp_json = json.loads(message)
                    # Organizing data for Pandas Dataframe
                    msg_data = []
                    time_id = []
                    curr_dt = None
                    if first == False:
                        if temp_json['data']['e'] == "24hrTicker":
                            print(temp_json['data']["E"])
                            curr_dt = datetime.fromtimestamp(temp_json['data']["E"]/1000)
                            msg_data = {
                                    'exchange': 'binance',
                                    'ticker': self.coin_dict[temp_json['data']['s']], 
                                    'price': temp_json['data']['c']
                                }
                            time_id = [curr_dt]
                        if self.queue_1.full():
                                print('working 1')
                        if msg_data != [] and time_id != []:
                            df = pd.DataFrame(data=msg_data, index=time_id)
                            print(df)
                            self.queue_1.put(df) 
                        # If level 2 data
                        elif temp_json['data']['e'] == "depthUpdate":
                            print(temp_json['data']["E"])
                            curr_dt = datetime.fromtimestamp(temp_json['data']["E"]/1000)
                            for update in enumerate (temp_json['data']['b']):
                                msg_data = {
                                        'exchange': 'binance',
                                        'ticker': self.coin_dict[temp_json['data']['s']], 
                                        'side': "buy",
                                        'price': update[1][0],
                                        'quantity': update[1][1]
                                    }
                                time_id = [curr_dt]
                                if self.queue_2.full():
                                    print('working 2')
                                if msg_data != [] and time_id != []:
                                    df = pd.DataFrame(data=msg_data, index=time_id)
                                    print(df)
                                    self.queue_2.put(df) 
                            for update in enumerate (temp_json['data']['a']):
                                    msg_data = {
                                            'exchange': 'binance',
                                            'ticker': self.coin_dict[temp_json['data']['s']], 
                                            'side': "sell",
                                            'price': update[1][0],
                                            'quantity': update[1][1]
                                        }
                                    print(msg_data)
                                    time_id = [curr_dt]
                                    if self.queue_2.full():
                                        print('working 2')
                                    if msg_data != [] and time_id != []:
                                        df = pd.DataFrame(data=msg_data, index=time_id)
                                        print(df)
                                        self.queue_2.put(df) 
                    first = False
        except Exception:
            print(traceback.format_exc())

async def main(coins):
    q = multiprocessing.Queue()
    r = multiprocessing.Queue()
    bwr = BinanceWebSocket(q, r, coins)
    await bwr.run()  # TODO: Don't access private methods

q = multiprocessing.Queue()
r = multiprocessing.Queue()
coins = ['BTC-USDT', 'ETH-USDT']
bwr = BinanceWebSocket(q, r,coins)
bwr.run()


        
