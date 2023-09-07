import requests
import json

PAGE = 1
CHAIN = "ethereum"
URLS = {
    'ethereum': "https://etherscan.io/tokens.aspx/GetTokensBySubLabel",
}

LABEL = "stablecoin"
SUB_CATEGORY_ID = "0"


def generate_payload(page):
    payload = json.dumps({
        "dataTableModel": {
            "draw": 2,
            "columns": [
                {
                    "data": "number",
                    "name": "",
                    "searchable": True,
                    "orderable": False,
                    "search": {
                        "value": "",
                        "regex": False
                    }
                },
                {
                    "data": "contractAddress",
                    "name": "",
                    "searchable": True,
                    "orderable": False,
                    "search": {
                        "value": "",
                        "regex": False
                    }
                },
                {
                    "data": "tokenName",
                    "name": "",
                    "searchable": True,
                    "orderable": True,
                    "search": {
                        "value": "",
                        "regex": False
                    }
                },
                {
                    "data": "marketCap",
                    "name": "",
                    "searchable": True,
                    "orderable": True,
                    "search": {
                        "value": "",
                        "regex": False
                    }
                },
                {
                    "data": "holders",
                    "name": "",
                    "searchable": True,
                    "orderable": True,
                    "search": {
                        "value": "",
                        "regex": False
                    }
                },
                {
                    "data": "website",
                    "name": "",
                    "searchable": True,
                    "orderable": False,
                    "search": {
                        "value": "",
                        "regex": False
                    }
                }
            ],
            "order": [
                {
                    "column": 3,
                    "dir": "desc"
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
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'cookie': 'etherscan_cookieconsent=True; etherscan_address_format=0; etherscan_datetime_format=UTC; CultureInfo=en; displaymode=dim; __stripe_mid=6358dd39-4a45-4cdf-a51b-b1f2aa64284e948d32; etherscan_settings=x0:1|x1:1|x2:en|x3:USD|x4:0|x5:0|x6:ENS|x7:UTC|x8:0; etherscan_pwd=4792:Qdxb:e5RzxwPEz6t1giE73ZD3FS1hQDnwK5qNQtcbyYUhQUA=; etherscan_userid=rerakat332; etherscan_autologin=True; ASP.NET_SessionId=4ctajzmbtcmt0xnfvselz2ti; cf_clearance=S6vDALiWG.TAxpkOy.deGuTQRVEQXY0I.gSepOG.wuo-1694019552-0-1-dac0d38f.16bde013.8dc18c6f-150.2.1694018472; __cflb=02DiuFnsSsHWYH8WqVXcJWaecAw5gpnmetMbqovkRE6p4; __cuid=2b0ab155069c494ab647730188264955; amp_fef1e8=78c36e8c-82a3-49da-8bc1-4e17273b993dR...1h9lsvhhg.1h9lt05ih.10.6.16',
    'dnt': '1',
    'origin': 'https://etherscan.io',
    'pragma': 'no-cache',
    'referer': 'https://etherscan.io/tokens/label/energy-sector?subcatid=0&size=50&start=0&col=3&order=desc',
    'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
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
    with open(f"data/{CHAIN}/tkn_{LABEL}_{SUB_CATEGORY_ID}.json", "w") as f:
        json.dump(output, f, indent=4)
