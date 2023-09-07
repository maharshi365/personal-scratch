import argparse
import html
import json
import os
from pathlib import Path

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pymongo import MongoClient, InsertOne, UpdateOne

load_dotenv()


parser = argparse.ArgumentParser(
    prog='Label Inserter',
    description='Helps Insert Labels into MongoDB')

parser.add_argument(
    '--chain',
    help='Chain to insert labels for',
    required=True)
parser.add_argument(
    '--file',
    help='File to insert labels from',
    required=True)
parser.add_argument(
    '--definition',
    help='Definition to use',
    required=True)


args = parser.parse_args()

MONGO_URL = os.getenv('MONGO_URL')
MONGO_DB = os.getenv('MONGO_DB')
DEFINITION = args.definition.capitalize()

if not Path(args.file).is_file():
    raise Exception('File does not exist')

if not MONGO_URL or not MONGO_DB:
    raise Exception('Missing MONGO_URL, MONGO_DB')

client = MongoClient(MONGO_URL)
db = client[MONGO_DB]

LABEL_COLLECTION = db[f"{args.chain}-address-labels"]
DEFINITION_COLLECTION = db["label-definitions"]


print(f"Inserting labels for {args.chain} from {args.file}")

# make sure file is a json file
file_path = Path(args.file)
prefix = file_path.name.split('_')[0]
suffix = file_path.suffix

if suffix != '.json':
    raise Exception('File must be a json file')

if prefix not in ['acc', 'tkn']:
    raise Exception('File must start with acc_ or tkn_')

# open file
with open(file_path) as f:
    data = json.load(f)


def parse_account_file(data):
    parsed = []
    for entry in data:
        label, addressSoup = entry['nameTag'], BeautifulSoup(
            html.unescape(entry['address']), 'html.parser')

        label = label.replace(':', '')
        address = addressSoup.span.a['data-bs-title']

        if address and label:
            parsed.append({
                'label': label,
                'address': address.lower()
            })

    return parsed


parsers = {
    'acc': parse_account_file
}

if prefix not in parsers:
    raise Exception('Parser not built for this file')

parsed = parsers[prefix](data)


# find all the labels that already exist in the database
labels = [entry['label'] for entry in parsed]
existing = list(DEFINITION_COLLECTION.find({
    'type': DEFINITION,
    'label': {
        '$in': labels
    },
    'chain': args.chain
}))

print(f"Found {len(existing)}/{len(parsed)} existing labels")

# create a list of labels that don't exist in the database
existing_labels = [entry['label'] for entry in existing]
new_labels = [entry for entry in parsed if entry['label']
              not in existing_labels]

# insert the new labels into the database incrementing the label id by 1
start = DEFINITION_COLLECTION.find_one({}, sort=[("_id", -1)])
start = start['_id'] + 1 if start else 1

print(f"Starting label id: {start}")

insertions = []
label_map = {}
for i, entry in enumerate(new_labels):
    insertions.append(
        InsertOne({
            '_id': start + i,
            'type': DEFINITION,
            'label': entry['label'],
            'isSearchable': False,
            'chains': [args.chain]
        })
    )

    label_map[entry['label']] = start + i


if len(insertions) > 0:
    res = DEFINITION_COLLECTION.bulk_write(insertions)
    print(
        f"Inserted {res.inserted_count} new labels, {res.modified_count} existing labels")


for label in existing:
    label_map[label['label']] = label['_id']


updates = []
for entry in parsed:
    updates.append(
        UpdateOne({
            '_id': entry['address'],
        }, {
            '$addToSet': {
                'labels': label_map[entry['label']]
            }
        }, upsert=True)
    )

if len(updates) > 0:
    res = LABEL_COLLECTION.bulk_write(updates)
    print(
        f"Inserted {res.upserted_count} new labels, {res.modified_count} existing labels")
