import json
from collections import Counter
from pprint import pprint as pp

with open('data/combined_wallet_labels.json', 'r') as f:
    data = json.load(f)


print(f"Total number of labels: {len(data)}")

# get a count of distinct label_type and count of each
label_types = Counter([d['document']['label_type'] for d in data])
pp(label_types)

# # get a count of distinct label_type and label_subtype and count of each
# label_types = Counter(
#     [(d['document']['label_type'], d['document']['label_subtype']) for d in data])
# pp(label_types)
