from abc import ABC
import asyncio


class WebsocketConsumer(ABC):
    async def _async_consume(self, data_queue: asyncio.Queue) -> None:
        """Takes queue of data and does work on that data.

        Parameters
        ----------
        data_queue : asyncio.Queue
            Queue containing market data
        """
        # Feel free to override to take more parameters
        raise NotImplementedError

    async def consume(self, ml1_data: asyncio.Queue,
                      ml2_data: asyncio.Queue) -> None:
        """Asyncronously starts tasks to process market level
        1 and 2 data. This function does no processing work.

        Parameters
        ----------
        ml1_data : asyncio.Queue
            Queue containing market level 1 data.
        ml2_data : asyncio.Queue
            Queue containing market level 2 data.
        """
        loop = asyncio.get_running_loop()

        tasks = [
            # Feel free to override functions to pass more params to async_consume
            loop.create_task(self._async_consume(ml1_data)),
            loop.create_task(self._async_consume(ml2_data))
        ]

        try:
            await asyncio.gather(*tasks)
        except Exception as _:
            await self._close()

    async def _close(self):
        """Handles all resource cleanup for consumer"""
        raise NotImplementedError
