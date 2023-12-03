from decimal import Decimal

import pandas as pd

df = pd.read_parquet('data/receipt.parquet')

df['blockNumber'].to_bytes(sz, 'little', signed=signed)
