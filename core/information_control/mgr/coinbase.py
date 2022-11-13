import asyncio
import json
import multiprocessing
from multiprocessing.sharedctypes import Value
import time
import traceback
from datetime import datetime
from time import time
from uuid import uuid4

import pandas as pd
import websockets

from .web_socket import WebSocket

import pika


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
        # self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        # self.channel = self.connection.channel()
        # self.channel.exchange_declare(exchange='coinbase', exchange_type='fanout')
   
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
                        # if self.queue_1.full():
                            # print('working 1')
                        if msg_data != [] and time_id != []:

                            # print(msg_data)
                            # df = pd.DataFrame(data=msg_data, index=time_id)
                            # print(df)
                            # self.channel.basic_publish(exchange='coinbase', routing_key='', 
                            # body=df.to_string())
                            # print(df)
                            await self.queue_1.put(msg_data) 
                    # If market 2 data
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
                        # if self.queue_2.full():
                            # print('working 2')
                        if msg_data != [] and time_id != []:
                            df = pd.DataFrame(data=msg_data, index=time_id)
                            # self.channel.basic_publish(exchange='coinbase', routing_key='', 
                            # body=df.to_string())
                            # print(df)
                            await self.queue_2.put(msg_data) 
        except Exception as e:
            print(traceback.format_exc())
            raise e
            
        

# from concurrent.futures import ProcessPoolExecutor, wait
# from multiprocessing import Process
# from aio_pika import DeliveryMode, ExchangeType, Message, connect

# async def test(q, r):
#     # print("Waiting for connection...")
#     connection = await connect("amqp://guest:guest@localhost/")
#     # print("Connection received!")

#     async with connection:
#         # Creating a channel
#         channel = await connection.channel()

#         logs_exchange = await channel.declare_exchange(
#             "coinbase", ExchangeType.FANOUT,
#         )

#         while True:
#             # print("looping")
#             try:
#                 x = q.get_nowait()
#                 q.task_done()
#                 # print(x)
#                 message = Message(
#                     bytes(x.to_string(), 'utf-8'),
#                     delivery_mode=DeliveryMode.PERSISTENT,
#                 )

#                 # Sending the message
#                 # print("sending x!!")
#                 await logs_exchange.publish(message, routing_key='info')
#             except:
#                 pass

#             # message = Message(
#             #     bytes(x.to_string(), 'utf-8'),
#             #     delivery_mode=DeliveryMode.PERSISTENT,
#             # )

#             # # Sending the message
#             # print("sending x!!")
#             # await logs_exchange.publish(message, routing_key='info')
#             y = await r.get()
#             # print(y)
#             r.task_done()

#             message = Message(
#                 bytes(y.to_string(), 'utf-8'),
#                 delivery_mode=DeliveryMode.PERSISTENT,
#             )
#             # print("sending y!!")
#             # await asyncio.sleep(0.5)
#             await logs_exchange.publish(message, routing_key='info')
#             # print("y sent!")

# async def get_data(q, r):
#     idx = 0
#     while True:
#         await asyncio.sleep(0.5)
#         await q.put(idx)
#         await r.put(idx)
#         idx += 1

# async def bruh():
#     q = asyncio.Queue()
#     r = asyncio.Queue()
#     coins = ['BTC-USDT', 'ETH-USDT']
#     cwr = CoinbaseWebSocket(q, r,coins)
#     # print('h2')
#     producers = [asyncio.create_task(cwr._run())]
#     # producers = [asyncio.create_task(get_data(q, r))]
#     consumers = [asyncio.create_task(test(q, r))]

#     await asyncio.gather(*producers)
#     # print('---- done producing')
 
#     # # wait for the remaining tasks to be processed
#     # await queue.join()
 
#     # # cancel the consumers, which are now idle
#     # for c in consumers:
#     #     c.cancel()
#     # await asyncio.gather(cwr._run(), test(q, r))

# # import asyncio, random
 
# # async def rnd_sleep(t):
# #     # sleep for T seconds on average
# #     await asyncio.sleep(t * random.random() * 2)
 
# # async def producer(queue):
# #     while True:
# #         # produce a token and send it to a consumer
# #         token = random.random()
# #         print(f'produced {token}')
# #         if token < .05:
# #             break
# #         await queue.put(token)
# #         await rnd_sleep(.1)
 
# # async def consumer(queue):
# #     while True:
# #         token = await queue.get()
# #         # process the token received from a producer
# #         await rnd_sleep(.3)
# #         queue.task_done()
# #         print(f'consumed {token}')
 
# # async def _main():
# #     queue = asyncio.Queue()
 
# #     # fire up the both producers and consumers
# #     producers = [asyncio.create_task(producer(queue))
# #                  for _ in range(3)]
# #     consumers = [asyncio.create_task(consumer(queue))
# #                  for _ in range(10)]
 
# #     # with both producers and consumers running, wait for
# #     # the producers to finish
# #     await asyncio.gather(*producers)
# #     print('---- done producing')
 
# #     # wait for the remaining tasks to be processed
# #     await queue.join()
 
# #     # cancel the consumers, which are now idle
# #     for c in consumers:
# #         c.cancel()

# def huh():
#     asyncio.run(bruh())


# # Test if it works!
# import time
# def main():
#     q = asyncio.Queue()
#     r = asyncio.Queue()
#     coins = ['BTC-USDT', 'ETH-USDT']
#     cwr = CoinbaseWebSocket(q, r,coins)
#     cwr.run()
#     # asyncio.run(bruh())
#     # p = Process(target=huh)
#     # p.start()
#     # children = multiprocessing.active_children()
#     # for child in children:
#     #     print(child.pid)

#     # time.sleep(5)
#     # p.terminate()
#     # p.join(timeout=1)

#     # print("OUT")
#     # p.terminate()
#     # p.join()

#     # with ProcessPoolExecutor() as executor:
#     #     future = executor.submit(cwr.run)
#     #     done, not_done = wait([future], return_when=FIRST_COMPLETED)

    


