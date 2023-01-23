from .websocket_consumer import WebsocketConsumer


class PrintWSConsumer(WebsocketConsumer):
    def __init__(self):
        pass

    async def _async_consume(self, data_queue):
        while True:
            data = await data_queue.get()
            print(data)
            data_queue.task_done()