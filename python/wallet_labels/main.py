import requests
import json
from pathlib import Path

url = "https://zm2vutojfqrc0k43p-1.a1.typesense.net/multi_search?x-typesense-api-key=v2zBdfBZhDirnXbzWWnu1NidkGc3sHkm"


def get_search(page):
    return {"searches": [{"query_by": "label,label_subtype", "num_typos": 1, "typo_tokens_threshold": 1,
                         "highlight_full_fields": "label,label_subtype", "collection": "blockchain_data", "q": "*", "page": page, "per_page": 250}]}


PAGE = 1
while True:
    print(f"Getting page {PAGE}")
    payload = get_search(PAGE)

    res = requests.request("POST", url, data=json.dumps(payload))

    if len(res.json()['results'][0]['hits']) == 0:
        break
    with open(f"data/wallet_labels_{PAGE}.json", 'w') as f:
        json.dump(res.json()['results'][0]['hits'], f, indent=4)
    PAGE += 1

# combine all files
data = []
for file in Path('data').glob('wallet_labels_*.json'):
    with open(file, 'r') as f:
        data.extend(json.load(f))

with open('data/combined_wallet_labels.json', 'w') as f:
    json.dump(data, f, indent=4)

# delete all other files
for file in Path('data').glob('wallet_labels_*.json'):
    file.unlink()
