# Dependencies
import asyncio
import json
import multiprocessing
import time
import traceback
from datetime import datetime

#import websockets
from web_socket import WebSocket
from websockets import connect
import pandas as pd

# Build Kraken Websocket Class
class KrakenWebSocket(WebSocket):
    def __init__(self, queue_1, queue_2, coins=[]):

        """Passing queue_1, queue_2, coins, setting subscription message and channels to subscribe to
        
        Parameters
        queue_1 -> stores the multiprocessing queue that stores market level 1 data (see Coinbase_Websocket.py)
        queue_2 -> stores the multiprocessing queue that stores market level 2 data (ditto)
        coins -> stores strings that each represent crypto tickers 
        """
        self.queue_1 = queue_1
        self.queue_2 = queue_2
        self.coins = coins

        self.channels = ['ticker', 'trade']

        self.subscribe_message = self.on_open()

##The API client must request an authentication "token" via the following REST API endpoint "GetWebSocketsToken" 
#to connect to WebSockets Private endpoints.??

def on_open(self):
        #Generates a subscribe message to be converted into json to be sent to endpoint

        subscribe_message = {"channelID": 10001,
                             "channelName": self.channels,
                             "event": "subscriptionStatus",
                             "pair": self.coins,
                             "status": "subscribed",
                             "subscription": {
                                 "name": self.channels
                             }
                            }

        return subscribe_message


async def _run(self):  # Full Asynchronous Run
    try:
        async with websockets.connect('wss://ws-auth.kraken.com', max_size = 1000000000) as websocket:
            await websocket.send(json.dumps(self.subscribe_message))
            while True:
                message = await websocket.recv()
                temp_json = json.loads(message)

                # Organizing Data for pandas DataFrame
                msg_data = []
                time_stamp = []
                current_date = None

                #Market Data 1
                if temp_json['name'] == 'ticker':
                    msg_data = {
                        'exchange': 'kraken',
                        'ticker': temp_json[-1],
                        'close_price': temp_json[4][0],
                        'volume_today': temp_json[5][0]
                    }
                    #there was no time stamp, so just use current date I guess
                    current_date = datetime.now()
                    time_stamp = [current_date]

                    if self.queue_1.full():
                        print('working 1')

                    if msg_data != [] and time_stamp != []:
                        df = pd.DataFrame(data=msg_data, index=time_stamp)
                        print(df)
                        self.queue_1.put(df) 


                #Market Data 2 - trade
                elif temp_json['name'] == 'trade':
                    msg_data = {
                        'exchange': 'kraken',
                        'ticker': temp_json[-1],
                        'price': temp_json[1][0][0],
                        'volume': temp_json[1][0][1],
                        'type': temp_json[1][0][3]
                    }

                    current_date  = datetime.fromtimestamp(temp_json[1][0][2])
                    time_stamp = [current_date]

                    if self.queue_2.full():
                        print('working 2')

                    if msg_data != [] and time_stamp != []:
                        df = pd.DataFrame(data=msg_data, index=time_stamp)
                        print(df)
                        self.queue_2.put(df)

    except Exception:
        print(traceback.format_exc())

# Async Script Start
async def main(coins): 
    q = multiprocessing.Queue()
    r = multiprocessing.Queue()
    cwr = KrakenWebSocket(q, r, coins)
    await cwr._run()  # TODO: Don't access private methods

q = multiprocessing.Queue()
r = multiprocessing.Queue()
coins = ['BTC-USDT', 'ETH-USDT']
cwr = KrakenWebSocket(q, r,coins)
cwr._run()
