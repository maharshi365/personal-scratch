import json

from bs4 import BeautifulSoup

with open('html/temp.html') as f:
    soup = BeautifulSoup(f, 'html.parser')


# get all tr elements
trs = soup.find_all('tr')

addresses = []
for tr in trs:
    tds = tr.find_all('td')
    link = tds[1].find('a').get('href')
    address = link.split('/')[-1]

    addresses.append(address.lower())

with open('data/ethereum/toptokens.json', 'w') as f:
    json.dump(addresses, f)
