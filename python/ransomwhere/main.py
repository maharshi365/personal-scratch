# Source: https://ransomwhe.re/

import json
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

import requests as re


@dataclass
class Transaction:
    hash: str
    time: int
    amount: int
    amountUSD: float


@dataclass
class Entity:
    address: str
    balance: int
    blockchain: str
    createdAt: datetime
    updatedAt: datetime
    family: str
    balanceUSD: float
    transactions: list[Transaction]


# API_URL = "https://api.ransomwhe.re/export"

with open("temp.json", "r") as f:
    data = json.load(f)
    data = data['result']

entities = []

for entity in data:
    transactions = []
    for transaction in entity["transactions"]:
        transactions.append(
            Transaction(
                hash=transaction["hash"],
                time=transaction["time"],
                amount=transaction["amount"],
                amountUSD=transaction["amountUSD"],
            )
        )

    entities.append(
        Entity(
            address=entity["address"],
            balance=entity["balance"],
            blockchain=entity["blockchain"],
            createdAt=datetime.strptime(
                entity["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            updatedAt=datetime.strptime(
                entity["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            family=entity["family"],
            balanceUSD=entity["balanceUSD"],
            transactions=transactions,
        )
    )

# get all unique blockchains

# get a list of addresses for each unique blockchain/family combination

addresses = defaultdict(lambda: defaultdict(set))

for entity in entities:
    addresses[entity.blockchain][entity.family].add(entity.address)


def serialize_sets(obj):
    if isinstance(obj, set):
        return list(obj)

    return obj


with open("addresses.json", "w") as f:
    json.dump(addresses, f, indent=4, default=serialize_sets)
