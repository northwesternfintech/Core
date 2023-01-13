import ccxt.async_support
import pandas as pd
import traceback
import asyncio
from datetime import datetime


class CCXTWebSocket():
    def __init__(self, exchange, queue_1, queue_2, coins):
        self.queue_1 = queue_1
        self.queue_2 = queue_2
        self.coins = coins
        self.maindf = pd.DataFrame()

    async def async_run(self):
        try:
            self.exchange = ccxt.async_support.kraken()
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
