import asyncio
import time
from datetime import datetime
from typing import List, Optional

import ccxt
import ccxt.async_support

from .websocket_consumers.websocket_consumer import WebsocketConsumer


class CCXTWebSocket:
    def __init__(self,
                 exchange: str,
                 tickers: List[str],
                 ws_consumer: WebsocketConsumer,
                 ml1_queue: Optional[asyncio.Queue] = asyncio.Queue(),
                 ml2_queue: Optional[asyncio.Queue] = asyncio.Queue(),
                 timeout: Optional[int] = None):
        """Class for pulling ticker information from an exchange using the CCXT
        library

        Parameters
        ----------
        exchange : str
            Name of exchange to use
        tickers : List[str]
            List of tickers to pull data for
        ws_consumer : WebsocketConsumer
            Consumer class that consumes ticker data
        ml1_queue: Optional[asyncio.Queue]
            Queue for market level 1 data. Optional unless you want to reuse the 
            same consumer
        ml2_queue: Optional[asyncio.Queue]
            Queue for market level 2 data. Optional unless you want to reuse the 
            same consumer
        timeout : Optional[int], optional
            How long to run websocket for. If none, then run forever, by default None

        Raises
        ------
        ValueError
            If given invalid CCXT exchange
        ValueError
            If given invalid ticker name for CCXT exchange
        """
        self._exchange_name = exchange
        self._tickers = tickers
        self._ws_consumer = ws_consumer
        self._timeout = timeout
        self._ml1_queue = ml1_queue
        self._ml2_queue = ml2_queue

        try:
            getattr(ccxt.async_support, self._exchange_name)
        except AttributeError:
            raise ValueError(f"Unrecognized exchange {self._exchange_name}")

        self._ccxt_exchange = getattr(ccxt, self._exchange_name)()
        self._ccxt_exchange.load_markets()

        available_markets = self._ccxt_exchange.markets
        for t in tickers:
            if t not in available_markets:
                raise ValueError(f"Invalid ticker {t}")

        self._kill = asyncio.Event()

    async def _produce_ml1(self):
        while not self._kill.is_set():
            t0 = time.time()
            ml1_data = await self._ccxt_exchange.fetchTickers(self._tickers)

            for coin in self._tickers:
                cur_time = datetime.fromtimestamp(
                    ml1_data[coin]["timestamp"] / 1000
                )

                if ml1_data and cur_time:
                    msg_data = {
                        "exchange": str(self._ccxt_exchange).split(". ")[0],
                        "ticker": coin,
                        "price": ml1_data[coin]["average"],
                        "time": cur_time
                    }
                    t0 = time.time()
                    await self._ml1_queue.put(msg_data)

    async def _produce_ml2(self):
        while not self._kill.is_set():
            for coin in self._tickers:
                ml2_data = await self._ccxt_exchange.fetchOrderBook(coin)
                cur_time = None
                if ml2_data["timestamp"]:
                    cur_time = datetime.fromtimestamp(
                        ml2_data["timestamp"] / 1000
                    )
                else:
                    cur_time = datetime.now()

                if ml2_data and cur_time:
                    bid = ml2_data['bids'][0][0] if ml2_data['bids'] else None
                    ask = ml2_data['asks'][0][0] if ml2_data['asks'] else None
                    spread = (ask - bid) if (bid and ask) else None

                    msg_data = {
                        "exchange": str(self._ccxt_exchange).split(". ")[0],
                        "ticker": coin,
                        "bid": bid,
                        "ask": ask,
                        "spread": spread,
                        "time": cur_time
                    }

                    await self._ml2_queue.put(msg_data)

    async def _timer(self):
        if self._timeout is None:
            return

        await asyncio.sleep(self._timeout)

        self._kill.is_set()

        await asyncio.sleep(1)
        self.shutdown()

    async def _run_async(self):
        self._ccxt_exchange = getattr(ccxt.async_support, self._exchange_name)()

        # self._ml1_queue = asyncio.Queue()
        # self._ml2_queue = asyncio.Queue()

        self._tasks = [
            asyncio.create_task(self._produce_ml1()),
            asyncio.create_task(self._produce_ml2()),
            asyncio.create_task(self._timer()),
            asyncio.create_task(self._ws_consumer.consume(self._ml1_queue,
                                                          self._ml2_queue))
        ]

        try:
            await asyncio.gather(*self._tasks)
        except asyncio.CancelledError:
            await self._close()

    async def _close(self):
        await self._ccxt_exchange.close()

    def shutdown(self):
        for task in self._tasks:
            task.cancel()

    def run(self):
        asyncio.get_event_loop().run_until_complete(self._run_async())


async def _main():
    from .websocket_consumers.websocket_consumer_factory import \
        WebsocketConsumerFactory

    # Initializing file writer
    ws_factory = WebsocketConsumerFactory()
    file_consumer = ws_factory.get("file")("test.csv", "test2.csv")

    # Creating queues for data
    q1 = asyncio.Queue()
    q2 = asyncio.Queue()

    # Creating web sockets
    ws = CCXTWebSocket("kraken", ["BTC/USD"], file_consumer, q1, q2, timeout=60)
    ws2 = CCXTWebSocket("kraken", ["ETH/USD"], file_consumer, q1, q2, timeout=60)

    # Creating async tasks
    t = [
        asyncio.create_task(ws._run_async()),
        asyncio.create_task(ws2._run_async())
    ]

    await asyncio.gather(*t)


def main():
    asyncio.run(_main())
