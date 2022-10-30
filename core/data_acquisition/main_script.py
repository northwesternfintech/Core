import concurrent.futures as cf
import multiprocessing as mp
import Kucoin_Websocket as ks
import Coinbase_Websocket as cb
import Gemini_Websocket as gm
import Binance_Websocket as bc
import Kraken_Websocket as kr  # TODO: Fix these imports, and just import the class "from kraken import KrakenWebSocket"
import pandas as pd
import asyncio
import schedule
import datetime
import os

async def main(coins):  # TODO: Don't think this needs to be async
    with cf.ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        pass


# Test if it works!
def activate(coins):
    if __name__ == '__main__':
        asyncio.get_event_loop().run_until_complete(main(coins))

coins = ['BTH-USDT']
activate(coins)