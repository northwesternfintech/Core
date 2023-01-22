import ujson
import zmq.asyncio
import zmq

from .websocket_consumer import WebsocketConsumer


class ZmqWSConsumer(WebsocketConsumer):
    def __init__(self, address: str):
        self._address = address

        self._context = zmq.asyncio.Context()
        self._pub_scoket = self._context.socket(zmq.PUB)
        self._pub_scoket.connect(address)


    async def _async_consume(self, data_queue):
        while True:
            data = await data_queue.get()
            ticker = data['ticker']
            msg = [ticker.encode('utf-8'), ujson.dumps(data).encode('utf-8')]
            await self._pub_socket.send_multipart(msg)
            data_queue.task_done()