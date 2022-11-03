import asyncio
from .coinbase import CoinbaseWebSocket
import multiprocessing
from aio_pika import DeliveryMode, ExchangeType, Message, connect
from typing import Dict, List, Optional, Union, Set, Tuple

import argparse


class WebSocketWorker:
    """Worker class for running a producer/consumer for 
    web sockets.
    """
    def __init__(self, address, port):
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

            logs_exchange = await channel.declare_exchange(
                "coinbase", ExchangeType.FANOUT,
            )

            while True:
                try:
                    ml1_data = ml1_queue.get_nowait()
                    ml1_queue.task_done()
                    message = Message(
                        bytes(mlw_data.to_string(), 'utf-8'),
                        delivery_mode=DeliveryMode.PERSISTENT,
                    )

                    await logs_exchange.publish(message, routing_key='info')
                except:
                    pass

                ml2_data = await ml2_queue.get()
                ml2_queue.task_done()

                message = Message(
                    bytes(ml2_data.to_string(), 'utf-8'),
                    delivery_mode=DeliveryMode.PERSISTENT,
                )
                await logs_exchange.publish(message, routing_key='info')


    async def run_async(self, tickers):
        """Awaits web socket and consumer tasks asynchronously.

        Parameters
        ----------
        tickers : _type_
            _description_
        """
        ml1_queue = asyncio.Queue()
        ml2_queue = asyncio.Queue()
        cwr = CoinbaseWebSocket(ml1_queue, ml2_queue, tickers)
        producers = [asyncio.create_task(cwr._run())]
        consumers = [asyncio.create_task(self.consume(ml1_queue, ml2_queue))]

        await asyncio.gather(*producers)


    def run(self, tickers: List[str]) -> None:
        """Wrapper class for starting asynchronous functions.

        Parameters
        ----------
        tickers : List[str]
            _description_
        """
        asyncio.run(self.run_async(tickers))


def cli_run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tickers", nargs="*", required=True, help="Tickers to run in websocket"
    )
    args = parser.parse_args()

    worker = WebSocketWorker(None, None)
    worker.run(args.tickers)

    
