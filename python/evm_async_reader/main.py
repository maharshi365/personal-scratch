import asyncio
import time

import orjson
from aiohttp import ClientSession, TCPConnector
from aiolimiter import AsyncLimiter
from web3 import AsyncHTTPProvider, AsyncWeb3
from web3.method import Method


class EVMApi:
    def __init__(self, rpc_url: str, rate: int):  # rate in requests per second
        self.rpc_url = rpc_url
        self.rate_limit = AsyncLimiter(rate, 1)

        self._api = AsyncWeb3(AsyncHTTPProvider(self.rpc_url, request_kwargs={
            "timeout": 60
        }))

        self._add_custom()  # Must be after _connect() as attach() depends on _api
        return

    def _add_custom(self):
        # Add self._api.eth.get_block_receipts -> eth_getBlockReceipts
        self._api.eth.attach_methods({
            "get_block_receipts": Method(
                "eth_getBlockReceipts"
            )
        })

        self._api.eth.attach_methods({
            "trace_block": Method(
                "trace_block"
            )
        })

        return

    async def fetch_block(self, block_number: int):
        await self.rate_limit.acquire()
        return await self._api.eth.get_block(block_number, full_transactions=True)

    async def fetch_traces(self, block_number: int):
        await self.rate_limit.acquire()
        return await self._api.eth.trace_block(f"{block_number:#x}")

    async def fetch_receipts(self, block_number: int):
        await self.rate_limit.acquire()
        return await self._api.eth.get_block_receipts(f"{block_number:#x}")

    async def fetch_full_block(self, block_number: int):
        # print(f"Fetching block {block_number}")
        # create a task for each of the three calls and wait for them to finish
        block_task = asyncio.create_task(self.fetch_block(block_number))
        traces_task = asyncio.create_task(self.fetch_traces(block_number))
        receipts_task = asyncio.create_task(self.fetch_receipts(block_number))

        await asyncio.wait([block_task, receipts_task, traces_task])

        block = block_task.result()
        traces = traces_task.result()
        receipts = receipts_task.result()

        # print(f"Block {block_number} fetched")
        return block, receipts, traces

    async def fetch(self):
        i = 17_000_000
        batch_size = 10
        while True:
            # fetch full blocks in batches
            start_time = time.time()
            tasks = [asyncio.create_task(
                self.fetch_full_block(i + j)) for j in range(batch_size)]

            await asyncio.wait(tasks)

            # for task in tasks:
            #     block, receipts, traces = task.result()
            #     print(
            #         f"Block {block['number']}: {len(block['transactions'])} transactions, {len(receipts)} receipts, {len(traces)} traces")
            end_time = time.time()

            print(
                f"Batch size: {batch_size}, Total time: {end_time - start_time:.2f}s, Average time per block: {(end_time - start_time) / batch_size:.2f}s")

            i += batch_size


async def main():
    api = EVMApi('https://eth-mainnet.blastapi.io/83176b15-8bc9-484e-8ccc-49add34034ac',
                 2000)

    await api._api.provider.cache_async_session(ClientSession(
        connector=TCPConnector(limit=None)
    ))

    await api.fetch()


if __name__ == '__main__':
    asyncio.run(main())
