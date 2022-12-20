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
import threading

async def main(coins):  # TODO: Don't think this needs to be async
    with cf.ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:

        # Initializing the multiprocessing queues for the websockets to use
        queue_lvl1 = multiprocessing.Queue()
        queue_lvl2 = multiprocessing.Queue()

        async def queue_to_csv():
            pd.concat([queue_lvl1.get(), queue_lvl2.get()]).to_csv(r"/Users/jaypark/Downloads/btc_output.csv")
            await asyncio.sleep(0.1)

        loop = asyncio.get_event_loop()  # or asyncio.get_running_loop()

        timeout = 10
        timer = loop.call_later(timeout, lambda: asyncio.ensure_future(queue_to_csv()))
        # Time in seconds (14400 seconds is 4 hours)

        try:
            # Initializing web sockets as the program traverses through the try except
            # layer to avoid unnecessarily initializing websockets
            binance = BinanceWebSocket(queue_lvl1, queue_lvl2, coins)
            executor.submit(await binance.run())
        except Exception as e:
            try:
                coinbase = CoinbaseWebSocket(queue_lvl1, queue_lvl2, coins)
                executor.submit(await coinbase.run())
            except Exception as e:
                # Try another websocket that was initialized, and if that doesn't work, layer in another try-except
                # In the end, if none of the websockets work, use an API
                print("hi")

# Test if it works!
def activate(coins):
    if __name__ == '__main__':
        asyncio.get_event_loop().run_until_complete(main(coins))
        # main(coins)

coins = ['BTC-USDT', 'ETH-USDT']
activate(coins)