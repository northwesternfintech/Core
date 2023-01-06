import ccxt.async_support
from web_socket import WebSocket
import pandas as pd
import traceback
import asyncio
import multiprocessing
from datetime import datetime
import time


class ccxtws():

    def __init__(self, exchange, queue_1, queue_2, coins):
        # self.exchange = ccxt.async_support.kraken()
        self.queue_1 = queue_1
        self.queue_2 = queue_2
        self.coins = coins
        self.shittyCounter = 0
        self.maindf = pd.DataFrame()

    async def async_run(self):
        if True:
            pass
        else:
            print("No fetchTickers!")
            return
        try:
            self.exchange = ccxt.async_support.coinbase()
            while True:
                m1Data = await self.exchange.fetch_tickers(symbols=self.coins)
                msgData = {}
                currDateTime = []
                for coin in self.coins:
                    msgData = {
                        "exchange": str(self.exchange).split(". ")[0],
                        "ticker": coin,
                        "price": m1Data[coin]["average"],
                    }
                    timeStamp = m1Data[coin]["timestamp"]
                    currDateTime = datetime.fromtimestamp(
                        m1Data[coin]["timestamp"] / 1000
                    )
                    if msgData != {} and currDateTime != []:
                        tempDataFrame = pd.DataFrame(data=msgData, index=[currDateTime])
                        # path = "/Users/dpark/Downloads/"
                        # filename = "RAW_CSV_OUTPUT_" + str(time.time()) + ".csv"
                        self.maindf = pd.concat([self.maindf, tempDataFrame])
                        print(self.maindf)
                        self.queue_1.put(self.maindf)
                        # self.shittyCounter += 1
                        # if self.shittyCounter > 10:
                        #     self.maindf.to_csv(path + filename)
                        #     self.shittyCounter = 0

        except Exception:
            print(traceback.format_exc())
    def activate(self):
        asyncio.get_event_loop().run_until_complete(self.async_run())


if __name__ == "__main__":
    q = multiprocessing.Queue()
    r = multiprocessing.Queue()
    # ws = ccxtws('kraken', q, r, coins=["ETH/USDT", "BTC/USDT"])
    # ws.activate()
