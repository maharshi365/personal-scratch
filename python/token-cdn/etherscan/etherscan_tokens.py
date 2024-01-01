from bs4 import BeautifulSoup

BASE_URL = 'https://ftmscan.com'
CHAIN = 'fantom'

with open('data/table.html', 'r', encoding='utf-8') as f:
    data = f.read()


soup = BeautifulSoup(data, 'html.parser')

# find all the tr tags
trs = soup.find_all('tr')


output = []

for row in trs:
    tds = row.find_all('td')

    img_data = tds[1]

    # address is the a tag href in img_data
    address = img_data.find('a')['href']
    img = img_data.find('img')['src']

    address = address.split('/')[-1].lower()
    img = f"{BASE_URL}{img}"

    if 'empty' in img:
        continue

    output.append({
        'address': address,
        'img': img,
        'chain': CHAIN
    })

with open(f'data/{CHAIN}.csv', 'a') as f:
    for row in output:
        f.write(f"{row['address']},{row['img']},{row['chain']}\n")
