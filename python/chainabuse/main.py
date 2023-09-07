import requests
import json


URL = "https://www.chainabuse.com/api/graphql-proxy"
HEADERS = {
    'authority': 'www.chainabuse.com',
    'content-type': 'application/json',
}

# CONFIG
CHAIN = "ETH"
NUM_REPORTS = 50  # cant change this
OUT_FILE = f"data/{CHAIN}.json"

# Update these from the website
TOTAL_ITEMS = 27604
AFTER = "YXJyYXljb25uZWN0aW9uOjE0"


def get_payload():
    payload = {
        "query": "query GetReports($input: ReportsInput, $after: String, $before: String, $last: Float, $first: Float) {  reports(    input: $input    after: $after    before: $before    last: $last    first: $first  ) {    pageInfo {      hasNextPage      hasPreviousPage      startCursor      endCursor      __typename    }    edges {      cursor      node {        ...Report        __typename      }      __typename    }    count    totalCount    __typename  }}fragment Report on Report {  id  isPrivate  ...ReportPreviewDetails  ...ReportAccusedScammers  ...ReportAuthor  ...ReportAddresses  ...ReportEvidences  ...ReportCompromiseIndicators  ...ReportTokenIDs  ...ReportTransactionHashes  __typename}fragment ReportPreviewDetails on Report {  createdAt  scamCategory  categoryDescription  biDirectionalVoteCount  viewerDidVote  description  lexicalSerializedDescription  commentsCount  source  checked  __typename}fragment ReportAccusedScammers on Report {  accusedScammers {    id    info {      id      contact      type      __typename    }    __typename  }  __typename}fragment ReportAuthor on Report {  reportedBy {    id    username    trusted    __typename  }  __typename}fragment ReportAddresses on Report {  addresses {    id    address    chain    domain    label    __typename  }  __typename}fragment ReportEvidences on Report {  evidences {    id    description    photo {      id      name      description      url      __typename    }    __typename  }  __typename}fragment ReportCompromiseIndicators on Report {  compromiseIndicators {    id    type    value    __typename  }  __typename}fragment ReportTokenIDs on Report {  tokens {    id    tokenId    __typename  }  __typename}fragment ReportTransactionHashes on Report {  transactionHashes {    id    hash    chain    label    __typename  }  __typename}",
        "variables": {
            "input": {
                "chains": [
                    CHAIN
                ],
                "scamCategories": [],
                "orderBy": {
                    "field": "CREATED_AT",
                    "direction": "DESC"
                }
            },
            "first": NUM_REPORTS,
            "after": AFTER
        }
    }

    return payload


def process_edge(edgeData):
    return {
        "id": edgeData['node']['id'],
        "scamCategory": edgeData['node']['scamCategory'],
        "source": edgeData['node']['source'],
        "addresses": [
            address['address'].lower() for address in edgeData['node']['addresses'] if address['chain'] == CHAIN and address['address'] is not None
        ]
    }


file = open(OUT_FILE, "a")
file.write("[")
file.flush()

hasNextPage = True
processedItems = 0
while hasNextPage:
    try:
        response = requests.request(
            "POST", URL, headers=HEADERS, data=json.dumps(get_payload()))

        res = response.json()['data']['reports']

        # deal with pagination
        pagination = res['pageInfo']
        hasNextPage = pagination['hasNextPage']
        startCursor = pagination['startCursor']
        nextCursor = pagination['endCursor']

        AFTER = nextCursor

        # process edges
        edges = res['edges']
        data = [process_edge(edge) for edge in edges]

        for d in data:
            file.write(json.dumps(d))
            file.write(",")
            file.flush()

        processedItems += len(data)

        print(f"Processed {processedItems} / {TOTAL_ITEMS}")
        print(f"Start Cursor: {startCursor} | Next Cursor: {nextCursor}")

    except Exception as e:
        print(e)
        break

file.write("]")
file.close()
