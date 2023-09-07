#!/usr/bin/env python3

import asyncio
import aiohttp
import gc
import logging
import orjson
import os
import time

from aiohttp import web
from contextlib import suppress


MESSAGE_HEADER = {"jsonrpc": "2.0", "id": 0}


#
# Setup logger
#

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

logger.setLevel(os.environ.setdefault("LOG_LEVEL", "INFO"))


#
# Inline config
#

config = {
    "url": "",
    "workers": 100,
    "start_block": 12_000_000,
    "block_count": 100_000,
    "blocks_in_batch": 3,
    "timeout": 100,
    "retry_interval": 0.5,
    "stats_interval": 10,
}


#
# Globals
#

pending_block = config["start_block"]

response_queue = asyncio.Queue(100)


def get_batch_request(first_block, start_block, block_count, blocks_in_batch, **kwargs):
    batch_request = []

    last_block = min(first_block + blocks_in_batch, start_block + block_count)

    for block_number in range(first_block, last_block):
        block_batch_request = [
            {
                **MESSAGE_HEADER,
                "method": "trace_block",
                "params": [hex(block_number)],
            },
            {
                **MESSAGE_HEADER,
                "method": "eth_getBlockReceipts",
                "params": [hex(block_number)],
            },
            {
                **MESSAGE_HEADER,
                "method": "eth_getBlockByNumber",
                "params": [hex(block_number), True],
            },
        ]
        batch_request.extend(block_batch_request)
    return last_block, last_block - first_block, orjson.dumps([*batch_request])


async def send_request(session, request, url, timeout, retry_interval, **kwargs):
    while True:
        try:
            headers = {
                "content-type": "application/json",
                "accept": "application/json",
            }
            async with session.post(
                url,
                headers=headers,
                data=request,
                timeout=timeout,
                raise_for_status=True,
            ) as response:
                return await response.read()
        except Exception:
            logger.exception("Caught exception (retrying)")
            await asyncio.sleep(retry_interval)


async def request_executor(session, start_block, block_count, **kwargs):
    global pending_block

    last_block = start_block + block_count
    while pending_block < last_block:
        pending_block, blocks_in_batch, batch_request = get_batch_request(
            pending_block, **config
        )
        await response_queue.put(
            (blocks_in_batch, await send_request(session, batch_request, **config))
        )


async def response_consummer(stats_interval, **kwargs):
    start = time.time()

    processed_blocks = 0
    while True:
        blocks_in_batch, response = await response_queue.get()
        try:
            # Simulate some work
            orjson.loads(response)
        except Exception as ex:
            logger.exception("Caught exception (ignoring)")
        finally:
            processed_blocks += blocks_in_batch
            # Print some stats every few seconds
            end = time.time()
            if end - start > stats_interval:
                logger.info(
                    f"RETRIEVED: {processed_blocks} blocks in {round(end-start, 2)} sec, {round(processed_blocks/(end-start), 2)} blocks/sec"
                )
                processed_blocks = 0
                start = end
            response_queue.task_done()


async def ctx_cleanup(_):
    conn = aiohttp.TCPConnector(limit=config["workers"])
    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = [asyncio.create_task(response_consummer(**config))]
        for _ in range(config["workers"]):
            tasks.append(asyncio.create_task(
                request_executor(session, **config)))

        yield

        for task in tasks:
            task.cancel()
        with suppress(asyncio.CancelledError):
            await task


def main():
    logger.info(f"{config}")

    app = web.Application()

    app.cleanup_ctx.append(ctx_cleanup)

    web.run_app(app=app)

    # Prevents exceptions during shutdown
    gc.collect()


if __name__ == "__main__":
    main()
