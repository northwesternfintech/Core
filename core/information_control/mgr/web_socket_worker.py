import asyncio
from .coinbase import CoinbaseWebSocket
import multiprocessing
from aio_pika import DeliveryMode, ExchangeType, Message, connect
from typing import Dict, List, Optional, Union, Set, Tuple


class WebSocketWorker:
    def __init__(self, address, port):
        self._address = address
        self._port = port

    async def pull_data(self, ml1_queue, ml2_queue):
        # print("Waiting for connection...")
        connection = await connect("amqp://guest:guest@localhost/")
        # print("Connection received!")

        async with connection:
            # Creating a channel
            channel = await connection.channel()

            logs_exchange = await channel.declare_exchange(
                "coinbase", ExchangeType.FANOUT,
            )

            while True:
                # print("looping")
                try:
                    x = ml1_queue.get_nowait()
                    ml1_queue.task_done()
                    message = Message(
                        bytes(x.to_string(), 'utf-8'),
                        delivery_mode=DeliveryMode.PERSISTENT,
                    )

                    # Sending the message
                    # print("sending x!!")
                    await logs_exchange.publish(message, routing_key='info')
                except:
                    pass

                # message = Message(
                #     bytes(x.to_string(), 'utf-8'),
                #     delivery_mode=DeliveryMode.PERSISTENT,
                # )

                # # Sending the message
                # print("sending x!!")
                # await logs_exchange.publish(message, routing_key='info')
                y = await ml2_queue.get()
                ml2_queue.task_done()

                message = Message(
                    bytes(y.to_string(), 'utf-8'),
                    delivery_mode=DeliveryMode.PERSISTENT,
                )
                # print("sending y!!")
                # await asyncio.sleep(0.5)
                await logs_exchange.publish(message, routing_key='info')
                # print("y sent!")

    # @staticmethod
    async def run_async(self, tickers):
        ml1_queue = asyncio.Queue()
        ml2_queue = asyncio.Queue()
        cwr = CoinbaseWebSocket(ml1_queue, ml2_queue, tickers)
        producers = [asyncio.create_task(cwr._run())]
        consumers = [asyncio.create_task(self.pull_data(ml1_queue, ml2_queue))]

        await asyncio.gather(*producers)


    def run_process(self, tickers: List[str]) -> None:
        """Function to be run inside of a process. Responsible for 
        starting async tasks, updating async_tasks, updating status_dict.

        # TODO: See if you can add error handeling

        Parameters
        ----------
        sockets_to_start : List[str]
            Names of sockets to start. Callers of this function are 
            responsible for ensuring the validity of this parameter.
        queues : Dict[str, multiprocessing.Queue]
            Dictionary mapping web socket name to the name of queues 
            to place data in.
        status_dict : Dict[str, WebSocketEnum]
            Dictionary mapping web scoket name to web socket status.
        async_tasks : Dict[str, asyncio.Tasks]
            Dictionary mapping web socket name to Tasks.
        """
        # You may need more helper functions to do this
        # Some helpful stuff:
        # https://docs.python.org/3/library/asyncio-task.html
        # create_task, as_completed
        asyncio.run(self.run_async(tickers))


def main():
    w = WebSocketWorker(None, None)
    w.run_process(['BTC-USDT', 'ETH-USDT'])
    
