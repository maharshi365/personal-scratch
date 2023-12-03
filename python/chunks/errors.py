import json
import re
from collections import defaultdict

with open('data/ingestion.ethereum_chunk_details.json', 'r') as f:
    data = json.load(f)

error_map = defaultdict(list)

for chunk in data:
    for key, value in chunk['indexing_error'].items():
        val = value[-1]

        skips = ['OvercommitTracker', 'is locked by a concurrent client',
                 'failed at position', 'Remote end closed connection without response', 'clickhouse_connect.driver.exceptions.OperationalError', 'OverflowError']

        if any(skip in val for skip in skips):
            continue

        error_map[key].append(f'{chunk["_id"]}: {val}')


with open('data/errors.json', 'w') as f:
    json.dump(error_map, f, indent=4)

# regex to search for Memory limit (total) exceeded: would use x GiB in middle of string

# regex = re.compile(r'.*Memory limit \(total\) exceeded: would use \d+ GiB.*')

# attempted_gb = []

# for chunk in data:
#     for key, value in chunk['indexing_error'].items():
#         val = value[-1]

#         if 'Memory limit (total) exceeded' in val:
#             match = val.split('Memory limit (total) exceeded: would use ')[1]
#             gb = match.split(' GiB')[0]

#             attempted_gb.append(float(gb))


# print(min(attempted_gb), max(attempted_gb))
