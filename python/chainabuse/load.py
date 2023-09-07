from pymongo import MongoClient, UpdateOne
import os
import json
from collections import defaultdict
from pprint import pprint as pp


def format_category(cat_str):
    return " ".join(cat_str.lower().split("_")).title()


# DEFAULTS
# CONNECTION_STRING = 'mongodb+srv://maharshi-admin:qFFYWWw4ggc0PIFp@blockscope-contracts.gvnem.mongodb.net'
DATBASE = 'smdata-prod'

COLLECTIONS = {
    'ETH': "ethereum-address-labels",
    'POLYGON': "polygon-address-labels"
}
CHAIN_NAMES = {
    'ETH': "ethereum",
    'POLYGON': "polygon"
}


# USER INPUT VARIABLES
CHAIN = 'POLYGON'
FILE = f'data/{CHAIN}.json'

if CHAIN not in COLLECTIONS.keys():
    print("Invalid chain. Exiting...")
    exit()

if not os.path.exists(FILE):
    print("File not found. Exiting...")
    exit()

# load data into a dict of sets
data = defaultdict(set)

with open(FILE, "r") as f:
    json_data = json.load(f)

    for item in json_data:
        category = format_category(item['scamCategory'])
        for address in item['addresses']:
            data[category].add(address)

client = MongoClient(CONNECTION_STRING)
db = client[DATBASE]

label_defintions_col = db['label-definitions']
address_labels = db[COLLECTIONS[CHAIN]]

labels = list(data.keys())

pp(labels)

# get all label definitions from db with label in labels
label_defintions = label_defintions_col.find({"label": {"$in": labels}})
label_defintions = list(label_defintions)

id_map = {label_defintion['label']: label_defintion['_id']
          for label_defintion in label_defintions}

pp(id_map)

# make list of labels that don't exist in db
labels_to_add = [label for label in labels if label not in [
    label_defintion['label'] for label_defintion in label_defintions]]

if (len(labels_to_add) > 0):
    print(f"Adding {len(labels_to_add)} new labels to db...")

  # get max label id from the db
    max_label_id = label_defintions_col.find_one(sort=[("_id", -1)])
    max_label_id = max_label_id['_id']

    # create new label definitions
    new_label_defintions = []
    for label in labels_to_add:
        max_label_id += 1
        new_label_defintions.append({
            "_id": max_label_id,
            "label": label,
            "type": "Security",
            "chains": [CHAIN_NAMES[CHAIN]],
            "isSearchable": True
        })

    label_defintions_col.insert_many(new_label_defintions)

    # update id_map with new label definitions
    new_label_defintions = label_defintions_col.find(
        {"label": {"$in": labels_to_add}})
    new_label_defintions = list(new_label_defintions)
    id_map.update({label_defintion['label']: label_defintion['_id']
                  for label_defintion in new_label_defintions})

    pp(id_map)

# bulk write address labels to db
for key, value in data.items():
    label_id = id_map[key]
    print(f"Updating {len(value)} addresses for {key} with id {label_id}...")
    bulk_ops = []

    for address in value:
        bulk_ops.append(UpdateOne(
            {"_id": address},
            {"$addToSet": {"labels": label_id}},
            upsert=True
        ))

    res = address_labels.bulk_write(bulk_ops)

    print(
        f"Updated {res.modified_count} addresses. Added {res.upserted_count} new addresses.\n")
