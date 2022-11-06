import concurrent.futures as cf
import multiprocessing
import multiprocessing as mp
# from kucoin import KucoinWebSocket
from Websockets.coinbase import CoinbaseWebSocket
# from gemini import GeminiWebSocket
from Websockets.binance import BinanceWebSocket
# from kraken import KrackenWebSocket
import pandas as pd
import asyncio
import schedule
import datetime
import os

async def main(coins):  # TODO: Don't think this needs to be async
    with cf.ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:

        # Initializing the multiprocessing queues for the websockets to use
        queue_lvl1 = multiprocessing.Queue()
        queue_lvl2 = multiprocessing.Queue()

        try:
            # Initializing web sockets as the program traverses through the try except
            # layer to avoid unnecessarily initializing websockets
            coinbase = CoinbaseWebSocket(queue_lvl1, queue_lvl2, coins)
            executor.submit(coinbase.run())
        except Exception as e:
            try:
                binance = BinanceWebSocket(queue_lvl1, queue_lvl2, coins)
                executor.submit(binance.run())
            except:
                # Try another websocket that was initialized, and if that doesn't work, layer in another try-except
                # In the end, if none of the websockets work, use an API
                print("Need to use API")

# Test if it works!
def activate(coins):
    if __name__ == '__main__':
        asyncio.get_event_loop().run_until_complete(main(coins))

coins = ['BTH-USDT']
activate(coins)