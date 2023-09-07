import asyncio
import itertools
import logging
import os

import aiohttp

ID_COUNTER = itertools.count()

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s", level=logging.INFO
)


logger = logging.getLogger(__name__)

logger.setLevel(os.environ.setdefault("LOG_LEVEL", "INFO"))


def create_batch_request(start_block: int, end_block: int):
    batch = []

    for block_number in range(start_block, end_block):
        block_batch_request = [
            {
                "jsonrpc": "2.0",
                "method": "trace_block",
                "params": [hex(block_number)],
                "id": next(ID_COUNTER),
            },
            {
                "jsonrpc": "2.0",
                "method": "eth_getBlockReceipts",
                "params": [hex(block_number)],
                "id": next(ID_COUNTER),
            },
            {
                "jsonrpc": "2.0",
                "method": "eth_getBlockByNumber",
                "params": [hex(block_number), True],
                "id": next(ID_COUNTER),
            },
        ]

        batch.extend(block_batch_request)

    return


async def send_request(session: aiohttp.ClientSession, request, url, timeout, retry_interval, **kwargs):
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
