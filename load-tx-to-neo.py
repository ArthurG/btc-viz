from neo4j.v1 import GraphDatabase, basic_auth
from constants import *
import csv

driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "123123"))
session = driver.session()

with open(IN_TRANSACTION_CSV_LOCATION, 'rb') as tx_in_file:
    in_reader = csv.reader(tx_in_file, delimiter=",")
    for row in in_reader:
        session.run("""MERGE (wallet:Wallet {address: {address}})
                     MERGE (tx:Transaction {hash: {hash}})
                     CREATE (wallet) -[:SENT {satoshi: {amount}}] -> (tx)
                     """,
                  {"address": row[1], "hash": row[0], "amount": row[2]})

with open(OUT_TRANSACTION_CSV_LOCATION, 'rb') as tx_out_file:
    out_reader = csv.reader(tx_out_file, delimiter=",")
    for row in out_reader:
        session.run("""MERGE (wallet:Wallet {address: {address}})
                     MERGE (tx:Transaction {hash: {hash}})
                     CREATE (wallet) -[:RECEIVED {satoshi: {amount}}]-> (tx)
                     """,
                  {"address": row[1], "hash": row[0], "amount": row[2]})

session.close()
