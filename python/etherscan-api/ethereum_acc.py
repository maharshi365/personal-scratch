import requests
import json

PAGE = 1
CHAIN = "ethereum"
URLS = {
    'ethereum': "https://etherscan.io/accounts.aspx/GetTableEntriesBySubLabel",
}

LABEL = "uniswap"
SUB_CATEGORY_ID = "0"


def generate_payload(page):
    payload = json.dumps({
        "dataTableModel": {
            "draw": 2,
            "columns": [
                {
                    "data": "address",
                    "name": "",
                    "searchable": True,
                    "orderable": False,
                    "search": {
                        "value": "",
                        "regex": False
                    }
                },
                {
                    "data": "nameTag",
                    "name": "",
                    "searchable": True,
                    "orderable": False,
                    "search": {
                        "value": "",
                        "regex": False
                    }
                },
                {
                    "data": "balance",
                    "name": "",
                    "searchable": True,
                    "orderable": True,
                    "search": {
                        "value": "",
                        "regex": False
                    }
                },
                {
                    "data": "txnCount",
                    "name": "",
                    "searchable": True,
                    "orderable": True,
                    "search": {
                        "value": "",
                        "regex": False
                    }
                }
            ],
            "order": [
                {
                    "column": 1,
                    "dir": "asc"
                }
            ],
            "start": (page - 1) * 100,
            "length": 100,
            "search": {
                "value": "",
                "regex": False
            }
        },
        "labelModel": {
            "label": LABEL,
            "subCategoryId": SUB_CATEGORY_ID
        }
    })

    return payload


HEADERS = {
    'authority': 'etherscan.io',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'cookie': 'etherscan_cookieconsent=True; etherscan_address_format=0; etherscan_datetime_format=UTC; CultureInfo=en; displaymode=dim; __stripe_mid=6358dd39-4a45-4cdf-a51b-b1f2aa64284e948d32; etherscan_settings=x0:1|x1:1|x2:en|x3:USD|x4:0|x5:0|x6:ENS|x7:UTC|x8:0; etherscan_pwd=4792:Qdxb:e5RzxwPEz6t1giE73ZD3FS1hQDnwK5qNQtcbyYUhQUA=; etherscan_userid=rerakat332; etherscan_autologin=True; __cuid=2b0ab155069c494ab647730188264955; amp_fef1e8=78c36e8c-82a3-49da-8bc1-4e17273b993dR...1h9lsvhhg.1h9lt05ih.10.6.16; __cflb=02DiuFnsSsHWYH8WqVXbZzkeTrZ6gtmGUeEzuaufC3JFv; ASP.NET_SessionId=hvplq2n3lukctfjrapzb0lhh; cf_chl_2=f88bf78d4523026; cf_clearance=xmw5YBxDKhjYI3CSIOYLFkspug7KUyUzGJVOPXfVhTI-1695740878-0-1-fe4282b9.df7d1216.a943dd59-150.2.1695740860',
    'dnt': '1',
    'pragma': 'no-cache',
    'referer': 'https://etherscan.io/accounts/label/lido',
    'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Referer': 'https://etherscan.io/',
    'DNT': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'x-client-data': 'CI22yQEIprbJAQiKksoBCKmdygEIp/TKAQiSocsBCIWgzQEIusjNAQi5ys0BCIrTzQEYj87NAQ==',
    'origin': 'https://etherscan.io',
    'x-requested-with': 'XMLHttpRequest',
    'content-type': 'application/json'
}

RUN_FLAG = True

output = []
total = 0

while RUN_FLAG:
    response = requests.request(
        "POST", URLS[CHAIN], headers=HEADERS, data=generate_payload(PAGE))

    resData = response.json()['d']

    if len(resData['data']) == 0:
        RUN_FLAG = False
        break

    if PAGE == 1:
        total = resData['recordsTotal']

    output.extend(resData['data'])
    print(
        f"{PAGE:^6} Extracted {len(output)} records of {total} total records. {len(output) / total * 100:.2f}% complete.")

    PAGE += 1

if (len(output) > 0):
    with open(f"data/{CHAIN}/acc_{LABEL}_{SUB_CATEGORY_ID}.json", "w") as f:
        json.dump(output, f, indent=4)
