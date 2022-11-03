import asyncio
import sys

from aio_pika import DeliveryMode, ExchangeType, Message, connect


async def _main() -> None:
    # Perform connection
    connection = await connect("amqp://guest:guest@localhost/")

    async with connection:
        # Creating a channel
        channel = await connection.channel()

        logs_exchange = await channel.declare_exchange(
            "coinbase", ExchangeType.FANOUT,
        )

        message_body = b" ".join(
            arg.encode() for arg in sys.argv[1:]
        ) or b"Hello World!"

        message = Message(
            message_body,
            delivery_mode=DeliveryMode.PERSISTENT,
        )

        # Sending the message
        await logs_exchange.publish(message, routing_key="info")

        print(f" [x] Sent {message!r}")


def main():
    asyncio.run(_main())