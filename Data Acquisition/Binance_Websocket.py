#Dependencies
import asyncio
import websockets
import multiprocessing
import json
import pandas as pd
from datetime import datetime
from uuid import uuid4


#Build Websocket Class
class Binance_Websocket():

    def __init__(self, q1, q2, coins = []):
        self.q1 = q1
        self.q2 = q2
        self.coins = coins
        self.params = self.generate_params(coins)
        self.request = self.generate_request()

    def generate_params(self,coins): #Generate request paramaters
        if coins == []:
            # get all market tickers if no coin is specified
            return '!ticker@arr'
        params = []
        for coin in coins:
            params.append(coin.lower()+'@trade')
        return params

    def generate_request(self): #Send subscribe request to the endpoint.
        request = {}
        params = []
        for param in self.params:
            params.append(param)
        request["method"] = "SUBSCRIBE"
        request["params"] = params
        request["id"] = 1 #Internal ID, not used by us at this point. 
        return request

    async def run(self): #Full asynchronous run. 
        try:
            async with websockets.connect('wss://stream.binance.com:9443/ws') as websocket:
                 await websocket.send(json.dumps(self.request))
                 while True:
                        message = await websocket.recv()
                        temp_json = json.loads(message)

                        # Set variables that will be entered into DataFrame
                        msg_data = []
                        time_id = []
                        curr_dt = None


                        # If the request is a message, get the DateTime from the json
                        if len(temp_json) != 2:
                            curr_dt = datetime.utcfromtimestamp(temp_json['T']/1000).strftime('%Y-%m-%d %H:%M:%S')
                            msg_data = {
                                'exchange': 'binance',
                                'ticker': temp_json['s'], 
                                'price': temp_json['p'],
                            }

                        # Prep index for DataFrame
                            time_id = [curr_dt]

                        if self.q1.full():
                            print('working')

                        if msg_data != [] and time_id != []:
                            df = pd.DataFrame(data = msg_data, index = time_id)
                            print(df)
                            self.q1.put(df)

        except Exception:
            import traceback
            print(traceback.format_exc())
    
    #Non-Async Wrapper
    def start(self):
        self.run()

#Async Script Start
async def main(coins):
    q = multiprocessing.Queue()
    r = multiprocessing.Queue()
    bwr = Binance_Websocket(q, r, coins = coins)
    # this example's getting market tickers for the specified coin types here, per the doc of binance, tickers come once every sec
    # if need sth else(like order book) just change generate_params's '@ticker' to whatever u want
    # or leave coins empty to get all market tickers
    await bwr.run()

#Non-async wrapper so MP can run it. 
def run(coins = ['BTCUSDT','ETHUSDT']):
    asyncio.run(main(coins))

# run()
