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

def main():
    print("[*] Waiting for logs. To exit press CTRL+C")
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://127.0.0.1:55690")
    socket.setsockopt_string(zmq.SUBSCRIBE, "BTC-USDT")
    socket.setsockopt_string(zmq.SUBSCRIBE, "ETH-USDT")

    while True:
        string = socket.recv()
        print(string)

# def main():

#     context = zmq.Context()
#     socket = context.socket(zmq.SUB)

#     print("Collecting updates from weather server...")
#     socket.connect("tcp://localhost:5556")

#     # Subscribe to zipcode, default is NYC, 10001
#     zip_filter = sys.argv[1] if len(sys.argv) > 1 else "10001"
#     socket.setsockopt_string(zmq.SUBSCRIBE, '10001')

#     # Process 5 updates
#     total_temp = 0
#     while True:
#     # for update_nbr in range(5):
#         string = socket.recv_string()
#         zipcode, temperature, relhumidity = string.split()

#         print((f"Average temperature for zipcode " 
#         f"'{zip_filter}' {temperature} F"))