import json
import random

import pandas as pd
from bson import ObjectId

file = 'data/ethereum_errors.json'

with open(file, 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)


def parse_index_errors(df: pd.DataFrame, index_name: str, chain: str) -> None:
    # get me all the rows where the failed_indexes is [transaction_index]
    df = df[df['failed_indexes'].apply(lambda x: index_name in x)].copy()

    # get the last element of the indexing_error in the transaction_index key
    df['err'] = df['indexing_error'].apply(
        lambda x: x[index_name][-1].strip('\n') if x[index_name] else None)
    df['_id'] = df['_id'].apply(lambda x: str(ObjectId(x['$oid'])))
    df['failedCount'] = df['failed_indexes'].apply(lambda x: len(x))
    df.sort_values(by=['err', 'start_block'], inplace=True)
    df[['_id', 'start_block', 'end_block', 'failedCount', 'err', ]].to_csv(
        f"{chain}_{index_name}_errors.csv", index=False)


def get_rand_sample(file: str, error: str, items: int) -> list[dict]:
    df = pd.read_csv(file)

    df = df[df['err'] == error]

    # get the start and end block in random sample
    df = df.sample(n=items)

    df['status'] = 'pending'

    return df[['start_block', 'end_block', 'status']].to_dict('records')


out = get_rand_sample('ethereum_transaction_index_errors.csv',
                      "AttributeError: 'DataFrame' object has no attribute 'gasPrice'", 15)

with open('data/error_sample.json', 'w') as f:
    json.dump(out, f, indent=4)
