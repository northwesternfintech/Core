import argparse
import json
import logging
from .worker import Worker
from typing import List
import asyncio
import zmq.asyncio
import zmq

from .. import protocol

logger = logging.getLogger(__name__)


class BacktestWorker(Worker):
    """Worker class for running a backtester. Responsible for starting a docker 
    container containing a trading algorithm and pushing live/historical data to
    the container
    """
    def __init__(self,
                 worker_uuid: str,
                 manager_uuid: str,
                 broker_uuid: str,
                 broker_address: str,
                 mode: str,
                 exchange: str = None,
                 tickers: List[str] = None,
                 subscribe_address: str = None,
                 heartbeat_interval_s: int = 1,
                 heartbeat_timeout_s: int = 1,
                 heartbeat_liveness: int = 3,):
        super().__init__(worker_uuid,
                         manager_uuid,
                         broker_uuid,
                         broker_address,
                         heartbeat_interval_s,
                         heartbeat_timeout_s,
                         heartbeat_liveness)

        self._mode = mode
        self._exchange = exchange
        self._tickers = tickers
        self._subscribe_address = subscribe_address
        self._input_file_path = input_file_path

    async def _run_live(self, exchange, tickers, subscribe_address):
        if exchange is None:
            self._send_status_message(protocol.DIE, "Missing parameter 'exchange'")
            self._shutdown()
            return

        if tickers is None:
            self._send_status_message(protocol.DIE, "Missing parameter 'tickers'")
            self._shutdown()
            return

        if subscribe_address is None:
            self._send_status_message(protocol.DIE, "Missing parameter 'subscribe_address'")
            self._shutdown()
            return

        self._sub_socket = self._context.socket(zmq.SUB)
        self._sub_socket.subscribe(subscribe_address)

        for ticker in tickers:
            self._sub_socket.setsockopt(zmq.SUBSCRIBE, f"{exchange}_{ticker}".encode())

        while True:
            data = (await self._sub_socket.recv_multipart())[1]

            print(data)  # We will call algo/container here in the future

    async def _shutdown(self):
        if hasattr(self, "_sub_socket"):
            self._sub_socket.setsockopt(zmq.LINGER, 0)

        await super()._shutdown()

    async def _run_async(self):
        tasks = await super()._get_heartbeat_tasks()

        match self._mode:
            case "live":
                tasks.append(asyncio.create_task(self._run_live(self._exchage,
                                                                self._tickers,
                                                                self._subscribe_address)))
            case "historical":
                pass
            case _:
                self._send_status_message(protocol.DIE, f"Invalid mode {self._mode}")
                self._shutdown()

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
        "--worker-uuid", required=True,
        help="uuid of worker"
    )
    parser.add_argument(
        "--manager-uuid", required=True,
        help="uuid of manager"
    )
    parser.add_argument(
        "--broker-uuid", required=True,
        help="uuid of broker"
    )
    parser.add_argument(
        "--broker-address", required=True,
        help="Address of broker"
    )
    parser.add_argumet(
        "--mode", required=True,
        help="Mode of backtester (either 'live' or 'historical')"
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
    parser.add_argument(
        "--exchange", required=False,
        type=str, default=None,
        help="Exchange to pull data from for 'live' mode"
    )
    parser.add_argument(
        "--subscribe-address", required=False,
        type=str, default=None,
        help="Address to subscribe to for data in 'live' mode"
    )
    parser.add_argument(
        "--tickers", required=False,
        type=str, default=None, nargs=argparse.REMAINDER,
        help="Interval to send heartbeat at"
    )
    args = parser.parse_args()

    worker = BacktestWorker(args.worker_uuid,
                            args.manager_uuid,
                            args.broker_uuid,
                            args.broker_address,
                            args.mode,
                            exchange=args.exchange,
                            tickers=args.tickers,
                            subscribe_address=args.subscribe_address,
                            heartbeat_interval_s=args.heartbeat_interval_s,
                            heartbeat_timeout_s=args.heartbeat_timeout_s,
                            heartbeat_liveness=args.heartbeat_liveness)
    worker.run()

