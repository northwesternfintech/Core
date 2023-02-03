import ujson
import zmq
import zmq.asyncio

from .websocket_consumer import WebSocketConsumer


class ZmqWSConsumer(WebSocketConsumer):
    def __init__(self, context, address: str = "tcp://127.0.0.1:50002"):
        """Pushes data from asyncio queue to zmq publish socket.

        Parameters
        ----------
        address : str, optional
            Address to push to. Should include protocol, route, 
            and port, by default "tcp://127.0.0.1:50002"
        """
        self._address = address

        self._pub_socket = context.socket(zmq.PUB)
        self._pub_socket.connect(address)


    async def _async_consume(self, data_queue):
        while True:
            data = await data_queue.get()

            ticker = data['ticker']
            data['time'] = data['time'].isoformat()
            msg = [ticker.encode('utf-8'), ujson.dumps(data).encode('utf-8')]

            await self._pub_socket.send_multipart(msg)
            data_queue.task_done()