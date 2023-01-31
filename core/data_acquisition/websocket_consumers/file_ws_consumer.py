import asyncio
import os
from typing import List

import aiofiles

from .websocket_consumer import WebsocketConsumer


class FileWSConsumer(WebsocketConsumer):
    def __init__(self,
                 ml1_file_name: str,
                 ml2_file_name: str,
                 ml1_fields: List[str] = [],
                 ml2_fields: List[str] = [],
                 flush_rate=5):
        """Writes data from web socket to json

        Parameters
        ----------
        ml1_file_name : str
            Name of file to write market level 1 data to
        ml2_file_name : str
            Name of file to write market level 2 data to
        ml1_fields : List[str], optional
            List of headers for market level 1 data, by default []
        ml2_fields : List[str], optional
            List of headers for market level 2 data, by default []
        flush_rate : int, optional
            Number of lines to fetch from web socket before writing, by default 5
        """
        self._ml1_file_name = ml1_file_name
        self._ml2_file_name = ml2_file_name

        self._ml1_fields = ml1_fields
        self._ml2_fields = ml2_fields

        self._flush_rate = flush_rate

        if not self._ml1_fields:
            self._ml1_fields = ["exchange", "ticker", "price", "time"]

        if not self._ml2_fields:
            self._ml2_fields = [
                "exchange", "ticker", "bid", "ask", "spread", "time"
            ]

        if not os.path.exists(self._ml1_file_name):
            with open(self._ml1_file_name, "w") as f:
                f.write(", ".join(self._ml1_fields) + "\n")

        if not os.path.exists(self._ml2_file_name):
            with open(self._ml2_file_name, "w") as f:
                f.write(", ".join(self._ml2_fields) + "\n")

    async def _async_consume(self, file_name, fields, data_queue):
        buffer = []
        buffer_counter = 0

        while True:
            data = await data_queue.get()
            data_queue.task_done()

            data["time"] = data["time"].isoformat()
            buffer.append(data)
            buffer_counter += 1

            if buffer_counter >= self._flush_rate:
                async with aiofiles.open(file_name, "a") as f:
                    for line in buffer:
                        line_str = ", ".join([str(line[field]) for field in fields])
                        await f.write(line_str + "\n")

                buffer = []
                buffer_counter = 0

    async def consume(self, ml1_data: asyncio.Queue,
                      ml2_data: asyncio.Queue) -> None:
        loop = asyncio.get_running_loop()

        tasks = [
            loop.create_task(self._async_consume(self._ml1_file_name,
                                                 self._ml1_fields,
                                                 ml1_data)),
            loop.create_task(self._async_consume(self._ml2_file_name,
                                                 self._ml2_fields,
                                                 ml2_data))
        ]

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            await self._close()

    async def _close(self):
        pass
