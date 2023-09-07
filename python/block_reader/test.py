import requests
import json


URL = 'https://arbitrum-one.blastapi.io/83176b15-8bc9-484e-8ccc-49add34034ac'
BLOCK = 123418203


payload = {
    "jsonrpc": "2.0",
    "method": "trace_block",
    "params": [hex(BLOCK)],
    "id": 1
}

req = requests.post(URL, json=payload)
with open('trace_block.json', 'w') as f:
    json.dump(req.json(), f)


payload = {
    "jsonrpc": "2.0",
    "method": "eth_getBlockReceipts",
    "params": [hex(BLOCK)],
    "id": 1
}

req = requests.post(URL, json=payload)
with open('eth_getBlockReceipts.json', 'w') as f:
    json.dump(req.json(), f)


payload = {
    "jsonrpc": "2.0",
    "method": "eth_getBlockByNumber",
    "params": [hex(BLOCK), True],
    "id": 1
}

req = requests.post(URL, json=payload)
with open('eth_getBlockByNumber.json', 'w') as f:
    json.dump(req.json(), f)
