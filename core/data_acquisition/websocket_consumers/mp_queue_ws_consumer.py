import asyncio
import multiprocessing

from .websocket_consumer import WebsocketConsumer


class MpQueueWSConsumer(WebsocketConsumer):
    def __init__(self,
                 ml1_queue: multiprocessing.Queue,
                 ml2_queue: multiprocessing.Queue):
        """Pushes data from web socket to multiprocessing Queue.

        Parameters
        ----------
        ml1_queue : multiprocessing.Queue
            Multiprocessing queue for market level 1 data
        ml2_queue : multiprocessing.Queue
            Multiprocessing queue for market level 1 data
        """
        self._ml1_queue = ml1_queue
        self._ml2_queue = ml2_queue

    async def _async_consume(self, async_queue, mp_queue):

        while True:
            data = await async_queue.get()
            async_queue.task_done()

            mp_queue.put(data)

    async def consume(self, 
                      ml1_data: asyncio.Queue,
                      ml2_data: asyncio.Queue) -> None:
        loop = asyncio.get_running_loop()

        tasks = [
            loop.create_task(self._async_consume(ml1_data, self._ml1_queue)),
            loop.create_task(self._async_consume(ml2_data, self._ml2_queue))
        ]

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            await self._close()

    async def _close(self):
        pass
