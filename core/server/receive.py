
import asyncio

from aio_pika import ExchangeType, connect
from aio_pika.abc import AbstractIncomingMessage
import zmq
import sys


# async def on_message(message: AbstractIncomingMessage) -> None:
#     async with message.process():
#         print(f"[x] {message.body!r}")


# async def _main() -> None:
#     # Perform connection
#     connection = await connect("amqp://guest:guest@localhost/")

#     async with connection:
#         # Creating a channel
#         channel = await connection.channel()
#         await channel.set_qos(prefetch_count=1)

#         logs_exchange = await channel.declare_exchange(
#             "BTC-USDT", ExchangeType.FANOUT,
#         )

#         # Declaring queue
#         queue = await channel.declare_queue(exclusive=True)

#         # Binding the queue to the exchange
#         await queue.bind(logs_exchange)

#         # Start listening the queue
#         await queue.consume(on_message)

#         print(" [*] Waiting for logs. To exit press CTRL+C")
#         await asyncio.Future()


# def main():
#     asyncio.run(_main())

# def main():
#     print("[*] Waiting for logs. To exit press CTRL+C")
#     context = zmq.asyncio.Context()
#     socket = context.socket(zmq.SUB)
#     socket.connect("tcp://127.0.0.1:50002")
#     socket.setsockopt_string(zmq.SUBSCRIBE, "BTC-USDT")
#     socket.setsockopt_string(zmq.SUBSCRIBE, "ETH-USDT")

#     while True:
#         string = socket.recv()
#         print(string)

# import asyncio
# import zmq
# import zmq.asyncio

# async def recv_and_process():
#     ctx = zmq.asyncio.Context()
#     sock = ctx.socket(zmq.SUB)
#     sock.connect("tcp://127.0.0.1:50002")
#     sock.setsockopt_string(zmq.SUBSCRIBE, "BTC/USD")
#     while True:
#         _, msg = await sock.recv_multipart() # waits for msg to be ready
#         print(msg)

# def main():
#     asyncio.run(recv_and_process())

    #
##  Paranoid Pirate worker
#
#   Author: Daniel Lundin <dln(at)eintr(dot)org>
#

from random import randint
import time

import zmq

HEARTBEAT_LIVENESS = 3
HEARTBEAT_INTERVAL = 1
INTERVAL_INIT = 1
INTERVAL_MAX = 32

#  Paranoid Pirate Protocol constants
PPP_READY = b"\x01"      # Signals worker is ready
PPP_HEARTBEAT = b"\x02"  # Signals worker heartbeat

def worker_socket(context, poller):
    """Helper function that returns a new configured socket
       connected to the Paranoid Pirate queue"""
    worker = context.socket(zmq.DEALER) # DEALER
    identity = b"%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000))
    worker.setsockopt(zmq.IDENTITY, identity)
    poller.register(worker, zmq.POLLIN)
    worker.connect("tcp://localhost:5556")
    worker.send(PPP_READY)
    return worker


def run_worker(context):
    poller = zmq.Poller()

    liveness = HEARTBEAT_LIVENESS
    interval = INTERVAL_INIT

    heartbeat_at = time.time() + HEARTBEAT_INTERVAL

    worker = worker_socket(context, poller)
    cycles = 0
    while True:
        socks = dict(poller.poll(HEARTBEAT_INTERVAL * 1000))

        # Handle worker activity on backend
        if socks.get(worker) == zmq.POLLIN:
            #  Get message
            #  - 3-part envelope + content -> request
            #  - 1-part HEARTBEAT -> heartbeat
            frames = worker.recv_multipart()
            if not frames:
                break # Interrupted

            if len(frames) == 1 and frames[0] == PPP_HEARTBEAT:
                # print("I: Queue heartbeat")
                liveness = HEARTBEAT_LIVENESS

                # Simulate various problems, after a few cycles
                cycles += 1
                if cycles > 3 and randint(0, 4) == 0:
                    print("I: Simulating a crash")
                    break
                if cycles > 3 and randint(0, 4) == 0:
                    # print("I: Simulating CPU overload")
                    time.sleep(3)
                # print("I: Normal reply")
                worker.send_multipart(frames)
                liveness = HEARTBEAT_LIVENESS
                time.sleep(1)  # Do some heavy work
            else:
                print("E: Invalid message: %s" % frames)
            interval = INTERVAL_INIT
        else:
            liveness -= 1
            if liveness == 0:
                print("W: Heartbeat failure, can't reach queue")
                print("W: Reconnecting in %0.2fs..." % interval)
                time.sleep(interval)

                if interval < INTERVAL_MAX:
                    interval *= 2
                poller.unregister(worker)
                worker.setsockopt(zmq.LINGER, 0)
                worker.close()
                worker = worker_socket(context, poller)
                liveness = HEARTBEAT_LIVENESS
        if time.time() > heartbeat_at:
            heartbeat_at = time.time() + HEARTBEAT_INTERVAL
            # print("I: Worker heartbeat")
            worker.send(PPP_HEARTBEAT)


def main():
    context = zmq.Context(1)

    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor() as executor:
        for i in range(1000):
            executor.submit(run_worker, context)



# import zmq
# import zmq.asyncio
# import asyncio
# import time
# from core.data_acquisition.ccxt_websocket import CCXTWebSocket
# from typing import List

# from core.data_acquisition.websocket_consumers.websocket_consumer_factory import WebsocketConsumerFactory
# from .workers.worker import Worker


# class WebSocketWorker(Worker):
#     """Worker class for running a producer/consumer for
#     web sockets
#     """
#     def __init__(self,
#                  exchange: str,
#                  tickers: List[str], 
#                  publish_addres: str,
#                  worker_uuid,
#                  broker_address: str,
#                  heartbeat_interval_s: int = 1,
#                  heartbeat_timeout_s: int = 1, 
#                  heartbeat_liveness: int = 3,):
#         super().__init__(worker_uuid, 
#                          heartbeat_address, 
#                          heartbeat_interval_s, 
#                          heartbeat_timeout_s)

#     async def _handle_broker_messages(self):
#         """Polls socket for incoming messages. There are two types of 
#         messages:

#         1. Heartbeat: Replies to broker with heartbeat. If too many 
#         heartbeats are missed, assume broker is dead and die.
#         2. Kill: Begins shutdown process and sends acknowledgement 
#         to broker.
#         """
#         liveness = self._heartbeat_liveness
#         while not self._kill.is_set():
#             print("starting polling!")
#             socks = await self._poller.poll(self._heartbeat_timeout_s * 1000)
#             socks = dict(socks)

#             if socks.get(self._broker_socket) == zmq.POLLIN:
#                 print("received message!")
#                 frames = await self._broker_socket.recv_multipart()

#                 if not frames:
#                     print("Received empty frame")
#                     self._kill.set()
#                     break

#                 if len(frames) >= 3 and frames[0] == b"\x01" and frames[2] == b"KILL":
#                     print("received die")
#                     self._shutdown()
#                 elif len(frames) == 1 and frames[0] == b"\x02":
#                     print("received hearbeat")
#                     liveness = self._heartbeat_liveness
#                 else:
#                     print(frames)
#             else:
#                 print("received no heartbeat")
#                 liveness -= 1
#                 print(f"{liveness} lives left")

#                 if liveness == 0:
#                     self._kill.set()
#                     break

#         await self._shutdown()

#     async def _send_heartbeat(self):
#         self._broker_socket.send(b"\x01")
#         heartbeat_at = time.time() + self._heartbeat_interval_s

#         while not self._kill.is_set():
#             if time.time() > heartbeat_at:
#                 print("Sent heartbeat!")
#                 self._broker_socket.send(b"\x02")
#                 heartbeat_at = time.time() + self._heartbeat_interval_s
#             await asyncio.sleep(5e-2)

#     def _shutdown(self):
#         self._broker_socket.setsockopt(zmq.LINGER, 0)
#         self._broker_socket.close()

#         ws_socket = self._web_socket._ws_consumer._pub_socket
#         ws_socket.setsockopt(zmq.LINGER, 0)
#         ws_socket.close()

#         self._context.term()

#         self._web_socket._close()

#         for task in self._tasks:
#             task.cancel()

#     def _get_heartbeat_tasks(self):
#         self._tasks = [
#             asyncio.create_task(self._handle_broker_messages()),
#             asyncio.create_task(self._send_heartbeat()),
#             asyncio.create_task(self._web_socket._run_async())
#         ]

#         return self._tasks

#     async def _run_async(self):
#         """
#         Awaits web socket and consumer tasks asynchronously.
#         """
#         self._kill = asyncio.Event()

#         tasks = self._get_heartbeat_tasks()

#         try:
#             await asyncio.gather(*tasks)
#         except Exception as _:
#             return

#     def run(self):
#         asyncio.run(self._run_async())


# def main():
#     w = WebSocketWorker(
#         "abc123", "kraken", ["BTC/USD"], "tcp://localhost:5556", "tcp://127.0.0.1:50002"
#     )
#     w.run()