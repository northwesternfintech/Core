import asyncio
from .coinbase import CoinbaseWebSocket
import multiprocessing
from aio_pika import DeliveryMode, ExchangeType, Message, connect
from typing import Dict, List, Optional, Union, Set, Tuple

import argparse
import json

import sys
import os
import signal

class WebSocketWorker:
    """Worker class for running a producer/consumer for 
    web sockets.
    """
    def __init__(self, address, port, tickers):
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

    async def consume(self, ml1_queue, ml2_queue):
        """Consumes data produced by web socket and pushes it to broker.

        Parameters
        ----------
        ml1_queue : _type_
            _description_
        ml2_queue : _type_
            _description_
        """
        connection = await connect("amqp://guest:guest@localhost/")

        async with connection:
            channel = await connection.channel()

            ticker_exchanges = {}

            for ticker in self._tickers:
                ticker_exchanges[ticker] = await channel.declare_exchange(
                    ticker, ExchangeType.FANOUT,
                )

            while True:
                try:
                    ml1_data = ml1_queue.get_nowait()
                    ml1_queue.task_done()
                    message = Message(
                        bytes(json.dumps(ml1_data), 'utf-8'),
                        delivery_mode=DeliveryMode.PERSISTENT,
                    )

                    exchange = ticker_exchanges[ml1_data['ticker']]

                    await exchange.publish(message)
                except Exception as e:
                    pass

                ml2_data = await ml2_queue.get()
                ml2_queue.task_done()

                

                message = Message(
                    bytes(json.dumps(ml2_data), 'utf-8'),
                    delivery_mode=DeliveryMode.PERSISTENT,
                )

                exchange = ticker_exchanges[ml2_data['ticker']]

                await exchange.publish(message, routing_key='info')


    async def run_async(self):
        """Awaits web socket and consumer tasks asynchronously.

        Parameters
        ----------
        tickers : _type_
            _description_
        """
        ml1_queue = asyncio.Queue()
        ml2_queue = asyncio.Queue()
        cwr = CoinbaseWebSocket(ml1_queue, ml2_queue, self._tickers)
        tasks = [asyncio.create_task(cwr._run()),
                 asyncio.create_task(self.consume(ml1_queue, ml2_queue))]

        await asyncio.gather(*tasks)


    def run(self) -> None:
        """Wrapper class for starting asynchronous functions.

        Parameters
        ----------
        tickers : List[str]
            _description_
        """
        try:   
            asyncio.run(self.run_async())
        except Exception as e:
            print(e)
            os.kill(os.getpid(), signal.SIGTERM)


def cli_run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tickers", nargs="*", required=True, help="Tickers to run in websocket"
    )
    args = parser.parse_args()

    worker = WebSocketWorker(None, None, args.tickers)
    worker.run()

    
