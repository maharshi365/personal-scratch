import pandas as pd

csvs = [
    'data/ethereum.csv',
    'data/arbitrum.csv',
    'data/base.csv',
    'data/bsc.csv',
    'data/fantom.csv',
    'data/optimism.csv',
    'data/polygon.csv',
]

for csv in csvs:
    df = pd.read_csv(csv)
    old_shape = df.shape

    # Remove all rows with duplicate values in the 'address' column
    df = df.drop_duplicates(subset=['address'])

    new_shape = df.shape

    print(
        f'Old shape: {old_shape} | New shape: {new_shape} | Removed: {old_shape[0] - new_shape[0]}')

    # write to csv
    df.to_csv(csv, index=False)
