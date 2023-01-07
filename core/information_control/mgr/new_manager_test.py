import asyncio

async def run():
    for i in range(1):
        proc = await asyncio.create_subprocess_exec("new_worker_test")

def main():
    asyncio.run(run())