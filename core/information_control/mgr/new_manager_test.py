import asyncio
import sys
import time
from concurrent.futures import ProcessPoolExecutor, wait
from .new_backtest import backtest_test

# async def test():
#     loop = asyncio.get_running_loop()
#     print(id(loop))
#     with ProcessPoolExecutor() as pool:
#         print("running")
#         result = loop.run_in_executor(
#             pool, backtest_test)
#         print('custom process pool', result)

def main():
    # d = asyncio.run(test())
    p = ProcessPoolExecutor()
    p.submit(backtest_test)
    time.sleep(10)
    p.submit(backtest_test)
    # wait([x])
    # print(d)