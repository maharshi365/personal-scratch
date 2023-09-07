from pymongo import MongoClient
from dotenv import load_dotenv
import os
import argparse
from pathlib import Path

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

args = parser.parse_args()

MONGO_URL = os.getenv('MONGO_URL')
MONGO_DB = os.getenv('MONGO_DB')
MONGO_COLLECTION = f"{args.chain}-address-labels"

if not Path(args.file).is_file():
    raise Exception('File does not exist')

if not MONGO_URL or not MONGO_DB or not MONGO_COLLECTION:
    raise Exception('Missing MONGO_URL, MONGO_DB or MONGO_COLLECTION')

client = MongoClient(MONGO_URL)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]
