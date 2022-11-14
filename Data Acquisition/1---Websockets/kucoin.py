import asyncio
from time import time 
import websockets
import requests
import multiprocessing
import time
import json
from datetime import datetime
from uuid import uuid4
import pandas as pd
import traceback
from web_socket import WebSocket

class Kucoin_Websocket(WebSocket):

    def __init__(self, queue_1, queue_2, coins = []):
        self.token = ''
        super().__init__(queue_1, queue_2, coins)
        self.connectId = ''
        self.wsendpoint = ''
        self.timeout = 0
        self.level_1 = []
        self.level_2 = []
        self.coins = ['/market/ticker:' + ','.join(coins), '/market/level2:' + ','.join(coins)]
        for coin in coins:
            self.level_1.append('/market/ticker:' + coin)
            self.level_2.append('/market/level2:' + coin)
        self.last_ping = time.time()



    # getting websocket endpoint info / token information
    def get_info_ws(self):
        info = requests.post('https://api.kucoin.com/api/v1/bullet-public')
        info = info.json()
        self.token = info['data']['token']
        endpoint_tmp = info['data']['instanceServers'][0]['endpoint']
        self.timeout = int(info['data']['instanceServers'][0]['pingTimeout'] / 1000)
        self.connectId = str(uuid4()).replace('-', '')
        wsendpoint = f"{endpoint_tmp}?token={self.token}&[connectId={self.connectId}]"
        self.wsendpoint = wsendpoint
        
    # connecting webocket
    async def connect_ws(self):
        async with websockets.connect(self.wsendpoint) as websocket:
            data = await websocket.recv()
            data = json.loads(data)
            self.connectId = data["id"]
            await websocket.close()
    
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
            
    
    # Full Asynch Run
    async def _run(self):
        try:
            async with websockets.connect(self.wsendpoint, ping_interval=self.timeout, ping_timeout=None) as websocket:
                
                # Sending request for suscribe
                for coin in self.coins:
                    await websocket.send(json.dumps({
                        "id": self.connectId,
                        "type": 'subscribe',
                        "topic": coin,
                        "response": True
                    }))
                while True:

                    # Receive Message
                    data = await websocket.recv()
                    data = json.loads(data)
                    # Set variables that will be entered into DataFrame
                    msg_data = []
                    time_id = []
                    curr_dt = None

                    # Checking for type message
                    if data['type'] == 'message':
                        if data['topic'] in self.level_1:
                            curr_dt = datetime.utcfromtimestamp(data['data']['time']/1000).strftime('%Y-%m-%d %H:%M:%S')
                            tick_name = data['topic'].split("/")[2].split(':')[1]
                            msg_data = {
                                'exchange': 'kucoin',
                                'ticker': tick_name, 
                                'price': data['data']['price'],
                            }
                            time_id = [curr_dt]
                            if self.queue_1.full():
                                print('working')
                            if msg_data != [] and time_id != []:
                                df = pd.DataFrame(data=msg_data, index=time_id)
                                print('level 1')
                                print(df)
                                self.queue_1.put(df)

                        elif data['topic'] in self.level_2:
                            curr_dt = datetime.utcfromtimestamp(data['data']['time']/1000).strftime('%Y-%m-%d %H:%M:%S')
                            tick_name = data['topic'].split("/")[2].split(':')[1]

                            if data['data']['changes']['bids'] == []:
                                bid_price = ""
                                bid_size = ""
                                bid_seq = ""
                            else:
                                bid_price = data['data']['changes']['bids'][0][0]
                                bid_size = data['data']['changes']['bids'][0][1]
                                bid_seq = data['data']['changes']['bids'][0][2]
                            
                            if data['data']['changes']['asks'] == []:
                                ask_price = ""
                                ask_size = ""
                                ask_seq = ""
                            else:
                                ask_price = data['data']['changes']['asks'][0][0]
                                ask_size = data['data']['changes']['asks'][0][1]
                                ask_seq = data['data']['changes']['asks'][0][2]


                            msg_data = {
                                'exchange': 'kucoin',
                                'ticker': tick_name,
                                'ask_price': ask_price,
                                'ask_size': ask_size,
                                'ask_seq': ask_seq,
                                'bid_price': bid_price,
                                'bid_size': bid_size,
                                'bid_seq': bid_seq
                            }
                            time_id = [curr_dt]
                            if self.queue_2.full():
                                print('working 2')
                            if msg_data != [] and time_id != []:
                                df = pd.DataFrame(data=msg_data, index=time_id)
                                print("level 2")
                                print(df)
                                self.queue_2.put(df)
                    
        except Exception:
            print(traceback.format_exc())

    async def _main(self):
        # self.get_ws()
        # await self.get_id()
        # self.get_ws()
        # await self._run()

        self.get_info_ws()
        # await self.connect_ws()
        # print(self.coins)
        await self._run()



    def _run_(self):
        asyncio.run(self._main())

# Example Run
q = multiprocessing.Queue()
r = multiprocessing.Queue()
ws = Kucoin_Websocket(q, r, coins=['BTC-USDT', 'ETH-USDT'])
ws._run_()
