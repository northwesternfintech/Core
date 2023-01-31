from .websocket_consumer import WebsocketConsumer
from .print_ws_consumer import PrintWSConsumer
from .file_ws_consumer import FileWSConsumer
from .mp_queue_ws_consumer import MpQueueWSConsumer
from typing import Dict


class WebsocketConsumerFactory:
    def __init__(self):
        self._factory_map: Dict[str, WebsocketConsumer] = {
            "print": PrintWSConsumer,
            "file": FileWSConsumer,
            "mp_queue": MpQueueWSConsumer
        }

    def get(self, consumer_name: str) -> WebsocketConsumer:
        """Retrieves WebsocketConsumer subclass based on 
        identifier string.

        Parameters
        ----------
        consumer_name : str
            Name of websocket consumer to retrieve.

        Returns
        -------
        WebsocketConsumer
            Class (not instance) of websocket consumer.
        """
        if consumer_name not in self._factory_map:
            raise ValueError(f"{consumer_name} not recognized")

        return self._factory_map[consumer_name]
