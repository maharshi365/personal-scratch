import asyncio
import aiohttp
import time
import json
import math
import requests

URL = 'https://eth-mainnet.blastapi.io/83176b15-8bc9-484e-8ccc-49add34034ac'
RATE_LIMIT = 1000
CALLS_PER_BLOCK = 3
MAX_TASKS = math.floor(RATE_LIMIT / CALLS_PER_BLOCK) * CALLS_PER_BLOCK


request = [
    {
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": ["0x1126149", True],
        "id": "block-1"
    },
    {
        "jsonrpc": "2.0",
        'method': "trace_block",
        "params": ["0x1126149"],
        "id": "trace-1"

    },
    {
        "jsonrpc": "2.0",
        "method": "eth_getBlockReceipts",
        "params": ["0x1126149"],
        "id": "receipts-1"
    }
]

res = requests.post(URL, json=request)

with open('test.json', 'w') as f:
    json.dump(res.json(), f, indent=4)
