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

class Kucoin_Websocket():

    def __init__(self, queue_1, queue_2, coins = []):
        self.token = ''
        self.queue_1 = queue_1
        self.queue_2 = queue_2
        self.endpoint = ''
        self.connectid = ''
        self.wsendpoint = ''
        self.timeout = 0
        self.level_1 = []
        self.level_2 = []
        self.coins = ['/market/ticker:' + ','.join(coins), '/market/level2:' + ','.join(coins)]
        for coin in coins:
            self.level_1.append('/market/ticker:' + coin)
            self.level_2.append('/market/level2:' + coin)
        self.last_ping = time.time()

    #prereq function
    def get_ws(self):
        r = requests.post('https://api.kucoin.com/api/v1/bullet-public')
        r = r.json()
        self.token = r['data']['token']
        self.endpoint = r['data']['instanceServers'][0]['endpoint']
        self.timeout = int(r['data']['instanceServers'][0]['pingTimeout'] / 1000) - 2
        self.connectid = str(uuid4()).replace('-', '')
        wsendpoint = f"{self.endpoint}?token={self.token}&connectId={self.connectid}"
        self.wsendpoint = wsendpoint
        
    #prereq function 2
    async def get_id(self):
        async with websockets.connect(self.wsendpoint) as websocket:
            message = await websocket.recv()
            self.connectid = message.split(',')[0].split(':')[1].replace('"', '')
            await websocket.close()
            
    #woooo
    # do we need to rename this?
    async def _run(self):
        try:
            async with websockets.connect(self.wsendpoint, ping_interval=self.timeout, ping_timeout=None) as websocket:
                for coin in self.coins:
                    await websocket.send(json.dumps({
                        "id": self.connectid,
                        "type": 'subscribe',
                        "topic": coin,
                        "response": True
                    }))
                while True:
                    ### Formatting Stuff Starts Here
                    # Receive Message
                    message = await websocket.recv()
                    # Translate type str to json
                    temp_json = json.loads(message)
                    # Set variables that will be entered into DataFrame
                    msg_data = []
                    time_id = []
                    curr_dt = None
                    # If the request is a message, get the DateTime from the json
                    if temp_json['type'] == 'message':
                        if temp_json['topic'] in self.level_1:
                            curr_dt = datetime.utcfromtimestamp(temp_json['data']['time']/1000).strftime('%Y-%m-%d %H:%M:%S')
                            # Prep entry data for the DataFrame
                            tick_name = temp_json['topic'].split("/")[2].split(':')[1]
                            msg_data = {
                                'exchange': 'kucoin',
                                'ticker': tick_name, 
                                'price': temp_json['data']['price'],
                            }
                            # Prep index for DataFrame
                            time_id = [curr_dt]
                        # elif temp_json['topic'] == '/market/level2:BTC-USDT':
                        #     # Convert time to Datetime
                        #     curr_dt = datetime.utcfromtimestamp(temp_json['data']['sequenceEnd']/1000).strftime('%Y-%m-%d %H:%M:%S')
                        #     print(temp_json['data']['changes'])
                        #     if len(temp_json['data']['changes']['asks']) != 0 and len(temp_json['data']['changes']['bids']) != 0:
                        #         try:
                        #             # Prep entry data for DataFrame
                        #             msg_data = {
                        #                 'exchange': 'kucoin',
                        #                 'ticker': temp_json['subject'],
                        #                 'asks price': temp_json['data']['changes']['asks'][0][0],
                        #                 'asks size': temp_json['data']['changes']['asks'][0][1],
                        #                 'bids price': temp_json['data']['changes']['bids'][0][0],
                        #                 'bids size': temp_json['data']['changes']['bids'][0][1]
                        #             }
                        #             print(msg_data)
                        #             time_id = [curr_dt]
                        #         except:
                        #             print(traceback.format_exc())                                
                    if self.queue_1.full():
                        print('working')
                    # if self.queue_2.full():
                    #     print('working 2')
                    # If data is relevant, queue DataFrame
                    if msg_data != [] and time_id != []:
                        df = pd.DataFrame(data = msg_data, index = time_id)
                        print(df)
                        self.queue_1.put(df)
                    
        except Exception:
            # import traceback
            print(traceback.format_exc())

    async def _main(self):
        self.get_ws()
        await self.get_id()
        self.get_ws()
        await self._run()

    def _run_(self):
        asyncio.run(self._main())

# Example Run
# q = multiprocessing.Queue()
# r = multiprocessing.Queue()
# ws = Kucoin_Websocket(q, r, coins = ['BTC-USDT', 'ETH-USDT'])
# ws._run_()