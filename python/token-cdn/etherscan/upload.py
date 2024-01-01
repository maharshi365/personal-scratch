import json
import logging
import os
import random
import time

import boto3
import pandas as pd
import requests as r

#  setup file logging to logs/fetch.log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)

s3 = boto3.resource('s3')
bucket = s3.Bucket('blockscope-tokens')


"""
START EDITING BELOW
"""
CHAIN = 'bsc'
file = f'data/{CHAIN}.csv'
dirname, _ = os.path.split(__file__)

if not os.path.isfile(file):
    logging.error(f'File {file} does not exist')
    exit(1)

df = pd.read_csv(file)

for _, row in df.iterrows():

    address = row['address']
    thumbnail = row['source']

    if not thumbnail:
        logging.warning(f'No thumbnail for {address}')
        continue

    key = f'tokens/{CHAIN}/{address}/thumbnail.png'
    local_path = f'{dirname}/temp/{address}.png'

    try:
        with open(local_path, 'wb') as f:
            logging.info(
                f'Downloading thumbnail for {address} on chain {CHAIN}')

            res = r.get(thumbnail,  headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
            },
                stream=True)

            if res.status_code != 200:
                print(res.status_code)
                print(res.content)
                raise Exception('There is an issue. Chill out.')

            f.write(res.content)

        with open(local_path, 'rb') as f:
            bucket.upload_fileobj(f, key)
            logging.info(
                f'Uploaded thumbnail for {address} on chain {CHAIN}')

        os.remove(local_path)
    except Exception as e:
        logging.exception(
            f'Error uploading thumbnail for {address} on chain {CHAIN}')
    sleep = random.randint(1, 5)
    logging.info(f'Sleeping for {sleep} seconds')
    time.sleep(sleep)
