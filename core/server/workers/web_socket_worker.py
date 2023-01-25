import argparse
import asyncio
from typing import List

from ...data_acquisition.ccxt_websocket import CCXTWebSocket
from ...data_acquisition.websocket_consumers.zmq_ws_consumer import \
    ZmqWSConsumer
from .worker import Worker


class WebSocketWorker(Worker):
    """Worker class for running a producer/consumer for
    web sockets
    """
    def __init__(self,
                 exchange: str,
                 tickers: List[str],
                 publish_addres: str,
                 worker_uuid,
                 broker_address: str,
                 heartbeat_interval_s: int = 1,
                 heartbeat_timeout_s: int = 1,
                 heartbeat_liveness: int = 3,):
        super().__init__(worker_uuid,
                         broker_address,
                         heartbeat_interval_s,
                         heartbeat_timeout_s,
                         heartbeat_liveness)

        self._ws_consumer = ZmqWSConsumer(self._context, publish_addres)
        self._web_socket = CCXTWebSocket(exchange, tickers, self._ws_consumer)

    async def _shutdown(self):
        await self._web_socket._ccxt_exchange.close()
        self._ws_consumer._close()

        super()._shutdown()

    async def _run_async(self):
        tasks = super()._get_heartbeat_tasks()
        tasks.append(asyncio.create_task(self._web_socket._run_async()))

        try:
            await asyncio.gather(*tasks)
        except asyncio.exceptions.CancelledError:
            return
        except Exception as e:
            raise e

    def run(self):
        asyncio.run(self._run_async())


def cli_run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--exchange", required=True,
        help="Exchange to pull data from"
    )
    parser.add_argument(
        "--tickers", nargs="*", required=True,
        help="Tickers to run in websocket"
    )
    parser.add_argument(
        "--publish-address", required=True,
        help="Address to publish data to"
    )
    parser.add_argument(
        "--worker-uuid", required=True,
        help="uuid of worker"
    )
    parser.add_argument(
        "--broker-address", required=True,
        help="Address of broker"
    )
    parser.add_argument(
        "--heartbeat-interval-s", required=False,
        type=int, default=1,
        help="Interval to send heartbeat at"
    )
    parser.add_argument(
        "--heartbeat-timeout-s", required=False,
        type=int, default=1,
        help="Time to wait for heartbeat"
    )
    parser.add_argument(
        "--heartbeat-liveness", required=False,
        type=int, default=3,
        help="Max number of times to timeout before dying"
    )
    args = parser.parse_args()

    worker = WebSocketWorker(args.exchange,
                             args.tickers,
                             args.publish_address,
                             args.worker_uuid,
                             args.broker_address,
                             args.heartbeat_interval_s,
                             args.heartbeat_timeout_s,
                             args.heartbeat_liveness)
    worker.run()


def main():
    w = WebSocketWorker(
         "kraken", ["BTC/USD"], "tcp://localhost:5556", "abc123", "tcp://127.0.0.1:50002"
    )
    w.run()