from .websocket_consumer import WebSocketConsumer
from .print_ws_consumer import PrintWSConsumer
from .zmq_ws_consumer import ZmqWSConsumer
from typing import Dict


class WebSocketConsumerFactory:
    def __init__(self):
        self._factory_map: Dict[str, WebSocketConsumer] = {
            "print": PrintWSConsumer,
            "zmq": ZmqWSConsumer
        }

    def get(self, consumer_name: str) -> WebSocketConsumer:
        """Retrieves WebSocketConsumer subclass based on 
        identifier string.

        Parameters
        ----------
        consumer_name : str
            Name of websocket consumer to retrieve.

        Returns
        -------
        WebSocketConsumer
            Class (not instance) of websocket consumer.
        """
        if consumer_name not in self._factory_map:
            raise ValueError(f"{consumer_name} not recognized")

        return self._factory_map[consumer_name]
