#Dependencies
import asyncio
import websockets
import multiprocessing
import json
import pandas
import time
from datetime import datetime

# Creating Gemini websocket class
class Gemini_Websocket():

    def __init__(self, queue_1, queue_2, coins = []):
        self.queue_1 = queue_1
        self.queue_2 = queue_2
        self.coins = coins
        self.sub_msg_1 = self.on_open()[0]
        # self.sub_msg_1 = self.on_open[1]
        # self.update_message = self.update_response()

    #generates a subscribe message to be converted into json to be sent to endpoint
    def on_open(self):
        sub_msg_1 = {}
        sub_msg_1['type'] = 'subscribe'
        sub_msg_1['subscriptions'] = [{'name':'l2','symbols':self.coins}]
        # sub_msg_2 = {}
        # sub_msg_2['type'] = 'subscribe'
        # sub_msg_2['subscriptions'] = [{'name':'l1','symbols':self.coins}]
        return [sub_msg_1]
    
    async def run(self): #on_message, sends json subscription to endpoint and awaits response to be put into queue
        try:
            async with websockets.connect('wss://api.gemini.com/v2/marketdata') as websocket:
                await websocket.send(json.dumps(self.sub_msg_1))
                # await websocket.send(json.dumps(self.update_message))  #Takes around 20 seconds for update messages to show up...
                while True:
                    message = await websocket.recv()
                    temp_json = json.loads(message)
                    msg_data = []
                    time_id = []
                    curr_dt = None
                    # if the request is of type l2_updates (message for lvl2 market data), get the DateTime from the json
                    if 'result' in temp_json.keys() and temp_json['result'] == 'error':
                        pass
                    elif temp_json['type'] == 'l2_updates':
                        if 'trades' in temp_json.keys():
                        #check to see if timestamp is available to get
                            # if 'timestamp' in temp_json.get('trades')[0].keys():
                            curr_dt = datetime.fromtimestamp(temp_json['trades'][0]['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')
                            msg_data = {
                                'exchange': 'gemini',
                                'type': 'l2update',   
                                'ticker': temp_json['symbol'],
                                'side': temp_json['changes'][0][0],
                                'price': temp_json['changes'][0][1],
                                'quantity': temp_json['changes'][0][2]
                            }
                                # Prep index for DataFrame
                            time_id = [curr_dt]
                            if self.queue_2.full():
                                print('working')
                            if msg_data != [] and time_id != []:
                                # Create DataFrame
                                df = pandas.DataFrame(data = msg_data, index=time_id)
                                print(df)
                                # put the dataframe into the queue
                                self.queue_2.put(df)
                    elif temp_json['type'] == 'trade':
                        curr_dt = datetime.utcfromtimestamp(temp_json['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')
                        # print(temp_json)
                        msg_data = {
                                'exchange': 'Gemini',
                                'type': 'trade',
                                'ticker': temp_json['symbol'],
                                'side': temp_json['side'],
                                'price': temp_json['price'],
                                'quantity': temp_json['quantity']
                            }
                            # Prep index for DataFrame
                        time_id = [curr_dt]
                        if self.queue_2.full():
                            print('working')
                        if msg_data != [] and time_id != []:
                            # Create DataFrame
                            df = pandas.DataFrame(data = msg_data, index = time_id)
                            print(df)
                            # put the dataframe into the queue
                            self.queue_2.put(df)
                
        except Exception:
            import traceback
            print(traceback.format_exc())

    def start(self):
        self.run()
    
async def main(coins): 
    q = multiprocessing.Queue()
    r = multiprocessing.Queue()
    gws = Gemini_Websocket(q, r, coins)
    await gws.run()

# Notice: Non-Async Wrapper is required for multiprocessing to run
def run(coins = ['BTCUSD', 'ETHUSD']):
    asyncio.run(main(coins))
run()