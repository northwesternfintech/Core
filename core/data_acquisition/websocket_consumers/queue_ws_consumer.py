import multiprocessing
from .websocket_consumer import WebsocketConsumer


class QueueWSConsumer(WebsocketConsumer):
    def __init__(self):
        maxsize = 1024 # CHANGE THIS LATER ?? I don't know what this ideally should be
        self.mp_queues = multiprocessing.Queue(maxsize)
        pass

    async def _async_consume(self, data_queue):
        while True:
            data = await data_queue.get()
            self.mp_queues.put(data, True) # might need to change true to false later, idk
            print("Put into queue: ", data)
            # could be useful to call every time you add as a test - Queue.qsize() --> does not work on MacOS
            data_queue.task_done()