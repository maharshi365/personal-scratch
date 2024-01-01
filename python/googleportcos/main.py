import pandas as pd
from web3_input_decoder import decode_function

ABI = [
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "type": "string",
                "name": "company"
            }
        ],
        "name": "safeMint",
        "outputs": [],
        "type": "function"
    }
]


def get_company(df):
    decoded = decode_function(ABI, df['input'])

    return decoded[0][-1], decoded[1][-1]


df = pd.read_csv('data/list.csv')

df['recipient'], df['companyName'] = zip(*df.apply(get_company, axis=1))

# drop rows with duplicate company names
portocs = df.drop_duplicates(subset=['companyName'])
portocs[['recipient', 'companyName']].to_csv('data/portcos.csv', index=False)

df[['recipient', 'companyName']].to_csv('data/nft_holders.csv', index=False)
