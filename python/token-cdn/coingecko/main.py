import json
import logging
import os
import time

import boto3
import requests as r

#  setup file logging to logs/fetch.log

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)

PLATFORM_MAP = {
    'ethereum': 'ethereum',
    'polygon': 'polygon-pos',
}

s3 = boto3.resource('s3')
bucket = s3.Bucket('blockscope-tokens')


def get_token_thumbnail(chain: str, address: str) -> str:
    url = f'https://api.coingecko.com/api/v3/coins/{PLATFORM_MAP[chain]}/contract/{address}'

    response = r.get(url)

    if response.status_code == 429:
        raise Exception('Rate limited')

    if response.status_code != 200:
        logging.error(
            f'Error fetching token thumbnail for {address} on chain {chain}')
        return ''

    data = response.json()

    if 'image' not in data or 'thumb' not in data['image']:
        logging.error(
            f'Error fetching token thumbnail for {address} on chain {chain}')
        return ''

    return data['image']['thumb']


def read_json_file(filePath: str) -> list[str]:
    with open(filePath, 'r') as f:
        return json.load(f)


"""
START EDITING BELOW
"""
CHAIN = 'polygon'
FILE = f'data/{CHAIN}.json'
dirname, _ = os.path.split(__file__)


addresses = [address.lower() for address in read_json_file(FILE)]

print(f'Found {len(addresses)} addresses for chain {CHAIN}')
address = list(set(addresses))
print(f'Found {len(address)} unique addresses for chain {CHAIN}')

not_found = []
try:
    for idx, address in enumerate(addresses):
        if idx % 500 == 0:
            print(f'Starting {idx} of {len(addresses)}')

        logging.info(
            f'Fetching token thumbnail for {address} on chain {CHAIN}')

        thumbnail = None
        while thumbnail is None:
            try:
                thumbnail = get_token_thumbnail(CHAIN, address)
            except Exception as e:
                if 'Rate limited' in str(e):
                    logging.warning(
                        f'Rate limited, sleeping for 60 seconds')
                    time.sleep(60)

        if thumbnail == '' or thumbnail is None:
            not_found.append(address)
            continue

        logging.info(f'Uploading thumbnail for {address} on chain {CHAIN}')

        key = f'tokens/{CHAIN}/{address}/thumbnail.png'
        local_path = f'{dirname}/temp/{address}.png'

        try:
            with open(local_path, 'wb') as f:
                logging.info(
                    f'Downloading thumbnail for {address} on chain {CHAIN}')
                f.write(r.get(thumbnail).content)

            with open(local_path, 'rb') as f:
                bucket.upload_fileobj(f, key)
                logging.info(
                    f'Uploaded thumbnail for {address} on chain {CHAIN}')

            os.remove(local_path)
        except Exception as e:
            logging.exception(
                f'Error uploading thumbnail for {address} on chain {CHAIN}')
            not_found.append(address)

        time.sleep(5)

    with open(f'{dirname}/data/{CHAIN}-not-found.csv', 'a') as f:
        f.write('\n'.join(not_found))

    logging.info('Done')

except Exception as e:
    logging.exception(f'Error fetching token thumbnails for chain {CHAIN}')

except KeyboardInterrupt:
    with open(f'{dirname}/data/{CHAIN}-not-found.csv', 'a') as f:
        f.write('\n'.join(not_found))
    logging.info('Exiting')
