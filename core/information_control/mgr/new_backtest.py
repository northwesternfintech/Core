import asyncio
import time
import sys

async def counter():
    print(id(asyncio.get_running_loop()))
    for i in range(4):
        print(i)
        await asyncio.sleep(1)

def c():
    for i in range(20):
        print(i)
        time.sleep(1)


def backtest_test():
    # asyncio.run(counter())
    c()

    # return True
