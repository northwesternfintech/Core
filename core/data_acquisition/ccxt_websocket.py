import ccxt.async_support
import asyncio
from datetime import datetime
from typing import List


class CCXTWebSocket:
    def __init__(self, exchange: str,
                 coins: List[str],
                 ws_consumer):
        self._exchange_name = exchange
        self._coins = coins
        self._ws_consumer = ws_consumer

        try:
            getattr(ccxt.async_support, self._exchange_name)
        except AttributeError:
            raise ValueError(f"Unrecognized exchange {self._exchange_name}")

    async def _produce_ml1(self):
        while True:
            ml1_data = await self._ccxt_exchange.fetchTickers(self._coins)

            for coin in self._coins:
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

                    await self._ml1_queue.put(msg_data)

    async def _produce_ml2(self):
        while True:
            for coin in self._coins:
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

    async def _run_async(self):
        self._ccxt_exchange = getattr(ccxt.async_support, self._exchange_name)()

        self._ml1_queue = asyncio.Queue()
        self._ml2_queue = asyncio.Queue()

        tasks = [
            asyncio.create_task(self._produce_ml1()),
            asyncio.create_task(self._produce_ml2()),
            asyncio.create_task(self._ws_consumer.consume(self._ml1_queue,
                                                          self._ml2_queue))
        ]

        await asyncio.gather(*tasks)

    def run(self):
        asyncio.get_event_loop().run_until_complete(self._run_async())


def main():
    from .websocket_consumers.websocket_consumer_factory import WebsocketConsumerFactory
    ws_factory = WebsocketConsumerFactory()
    print_consumer = ws_factory.get("print")()
    ws = CCXTWebSocket("kraken", ["BTC/USD"], print_consumer)
    ws.run()
