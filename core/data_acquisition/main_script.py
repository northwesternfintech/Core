import concurrent.futures as cf
import multiprocessing
import multiprocessing as mp
import pandas as pd
import asyncio
import traceback
# import schedule
# import datetime
# import os
import ccxt
from ccxtpro_websocket.ccxttest import ccxtws
import time
import nest_asyncio

nest_asyncio.apply()


async def main(exchanges, coins):  # TODO: Don't think this needs to be async
    with cf.ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:

        # Initializing the multiprocessing queues for the websockets to use
        manager = multiprocessing.Manager()
        q = manager.Queue()
        r = manager.Queue()

        # async def queue_to_csv():
        #     # TODO: Replace the empty path string to the directory for desired output file
        #     path = "/Users/jaypark/Downloads/"
        #     filename = "RAW_CSV_OUTPUT_" + str(time.time()) + ".csv"
        #     pd.concat([q.get(), r.get()]).to_csv(path + filename)
        #     await asyncio.sleep(0.1)

        # loop = asyncio.get_event_loop()  # or asyncio.get_running_loop()

        # # Time in seconds (14400 seconds is 4 hours)
        # timeout = 10
        # timer = loop.call_later(timeout, lambda: asyncio.ensure_future(queue_to_csv()))

        # for i, exchange in enumerate(exchanges):
        try:
            # Initializing web sockets as the program traverses through the try except
            # layer to avoid unnecessarily initializing websockets
            # ws = ccxtws('ccxt.' + exchanges[0] + '()', q, r, coins)
            ws = ccxtws("fuck", q, r, coins=["ETH/USDT", "BTC/USDT"])
            future = executor.submit(ws.activate)
            while True:
                print(future)
                print(future.result())
                time.sleep(1)

        except Exception:
            traceback.print_exc()
            print("Need to use API")


# Test if it works!
def activate(exchanges, coins):
    if __name__ == "__main__":
        asyncio.get_event_loop().run_until_complete(main(exchanges, coins))


exchanges = ["kraken", "binance", "kucoin", "gemini", "coinbase"]
coins = ["BTC/USDT"]
(ccxt.kraken().fetchTickers(symbols=coins))
activate(exchanges, coins)
