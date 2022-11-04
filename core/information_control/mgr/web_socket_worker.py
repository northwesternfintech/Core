import argparse
import asyncio
import json
import os
import signal
from typing import List

from aio_pika import DeliveryMode, ExchangeType, Message, connect

from .coinbase import CoinbaseWebSocket


class WebSocketWorker:
    """Worker class for running a producer/consumer for
    web sockets.
    """
    def __init__(self, address, port, tickers: List[str]):
        """Creates a worker to run a web socket.

        Parameters
        ----------
        address : _type_
            _description_
        port : _type_
            _description_
        """
        self._address = address
        self._port = port
        self._tickers = tickers
        self._ticker_exchanges = {}

    async def _consume(self, queue):
        """Consumes data from a queue and pushes it to a broker.

        Parameters
        ----------
        queue : asyncio.Queue
            Queue to consume from.
        """
        connection = await connect("amqp://guest:guest@localhost/")
        channel = await connection.channel()
        ticker_exchanges = {}
        for ticker in self._tickers:
            ticker_exchanges[ticker] = await channel.declare_exchange(
                ticker, ExchangeType.FANOUT,
            )

        while True:
            data = await queue.get()
            queue.task_done()

            message = Message(
                bytes(json.dumps(data), 'utf-8'),
                delivery_mode=DeliveryMode.PERSISTENT,
            )
            exchange = ticker_exchanges[data['ticker']]

            await exchange.publish(message, routing_key='')

    async def _run_async(self):
        """
        Awaits web socket and consumer tasks asynchronously.
        """
        ml1_queue = asyncio.Queue()
        ml2_queue = asyncio.Queue()

        cwr = CoinbaseWebSocket(ml1_queue, ml2_queue, self._tickers)

        tasks = [asyncio.create_task(cwr._run()),
                 asyncio.create_task(self._consume(ml1_queue)),
                 asyncio.create_task(self._consume(ml2_queue))]

        await asyncio.gather(*tasks)

    def run(self) -> None:
        """
        Wrapper function for starting run_async.
        """
        try:
            asyncio.run(self.run_async())
        except Exception as e:
            print(e)
            os.kill(os.getpid(), signal.SIGTERM)


def cli_run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tickers", nargs="*", required=True,
        help="Tickers to run in websocket"
    )
    args = parser.parse_args()

    worker = WebSocketWorker(None, None, args.tickers)
    worker.run()
