import json
import re
from typing import Union

import requests

SDN_LIST_URL = 'https://www.treasury.gov/ofac/downloads/sdnlist.txt'
KEYWORDS = ['Digital Currency Address']
NETWORKS = ['XBT', 'LTC', 'ETH', 'ZEC', 'BSV', 'USDT', 'XRP',
            'TRX', 'DASH', 'BTG', 'ETC', 'XVG', 'ARB', 'XMR', 'BCH']


def format_response(res: str) -> list[str]:
    resSplit = res.splitlines()

    lines = []
    isEmpty = False

    for line in resSplit:
        if line != '':
            lines.append(line)
            isEmpty = False
        if line == '' and isEmpty == False:
            isEmpty = True
            lines.append(line)
        else:
            continue

    return lines


def merge_response_line(lines: list[str]) -> list[str]:
    mergedLines = []
    temp = ''

    for line in lines:
        if line != '':
            temp += line
        else:
            mergedLines.append(temp)
            temp = ''

    return mergedLines


def filter_keywords(lines: list[str]) -> list[str]:
    linesWithKeywords = []
    for line in lines:
        if any(keyword in line for keyword in KEYWORDS):
            linesWithKeywords.append(line)

    return linesWithKeywords


def clean_address(line: str) -> Union[dict[str, str], str]:
    if any(network in line for network in NETWORKS):
        # find the network
        network = ''
        for net in NETWORKS:
            if net in line:
                network = net
                break

        splitLine = line.split(network)
        address = splitLine[-1].strip().split(" ")[0].strip()
        return {'network': network, 'address': address}
    else:
        return line


def process_entry(lines: list[str]):
    output = []

    # name_regex is everything until first '(' or second ',' or first ';'
    name_regex = r'^(.*?)(?=[\(\,;])'
    for line in lines:
        search = re.search(name_regex, line)

        if not search:
            continue

        name = search.group(0).strip().replace('\"', '')

        # split the line by ';
        lines = line.split(';')

        # find all lines with Digital Currency Address
        filtered_lines = []
        for line in lines:
            if 'Digital Currency Address' in line:
                addr = line.split('Digital Currency Address -')[-1]
                filtered_lines.append(clean_address(addr))

        output.append({'name': name, 'addresses': filtered_lines})

    return output


res = requests.get(SDN_LIST_URL)
res = res.text
# with open('res.txt', 'r') as f:
#     res = f.read()

# format response
lines = format_response(res)
lines = merge_response_line(lines)
lines = filter_keywords(lines)
lines = process_entry(lines)

for line in lines:
    addresses = line['addresses']

    for addr in addresses:
        if isinstance(addr, str):
            print(addr)


# find lines with keywords
with open('data/sdnlist.json', 'w') as f:
    json.dump(lines, f)
