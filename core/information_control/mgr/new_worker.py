import asyncio
import sys

async def count():
    i = 0

    while True:
        print(i)
        await asyncio.sleep(1)
        i += 1
import time
def c():
    i = 0

    while True:
        print(i, flush=True)
        time.sleep(1)
        i += 1
        sys.stdout.flush()


def main():
    # asyncio.run(count())
    c()