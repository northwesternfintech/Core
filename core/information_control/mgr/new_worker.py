import asyncio

async def count():
    i = 0

    while True:
        print(i)
        await asyncio.sleep(1)
        i += 1

def main():
    asyncio.run(count())