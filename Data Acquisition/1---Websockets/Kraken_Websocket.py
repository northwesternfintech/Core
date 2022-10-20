# Dependencies
import asyncio
import websockets
import multiprocessing
import json

# Creating Kraken websocket class


class Kraken_Websocket():

    def __init__(self, queue, socket, coins=[]):
        self.queue = queue
        self.socket = socket
        self.coins = coins
        self.sub_message = self.on_open()

    def on_open(self):  # Generates a subscribe message to be converted into json to be sent to endpoint
        subscribe_message = {}
        subscribe_message["event"] = "subscribe"
        subscribe_message["subscription"] = {"name": "ticker"}
        pairs = []
        for coin in self.coins:
            pairs.append(coin)
        subscribe_message["pair"] = pairs
        return subscribe_message

    async def run(self):  # on_message, sends json subscription to endpoint and awaits response to be put into queue
        try:
            async with websockets.connect(self.socket) as websocket:
                await websocket.send(json.dumps(self.sub_message))
                while True:
                    message = await websocket.recv()
                    self.queue.put(message)
                    print('Kraken')
        except Exception:
            import traceback
            print(traceback.format_exc())

    def start(self):
        self.run()


async def main(coins):
    q = multiprocessing.Queue()
    socket = 'wss://ws.kraken.com/'
    kws = Kraken_Websocket(q, socket, coins)
    await kws.run()

# Notice: Non-Async Wrapper is required for multiprocessing to run


def run(coins=["XBT/USD", "XBT/EUR"]):
    asyncio.run(main(coins))


# run()
