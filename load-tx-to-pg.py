import psycopg2 
import csv
from constants import *

conn_string = ""

conn = psycopg2.connect("dbname='Transfers' user='arthur' host='localhost' password='123123'")

create = "CREATE TABLE transfers (tx_hash VARCHAR(255), wallet_addr VARCHAR(255), amount BIGINT, type VARCHAR(255))"
cur = conn.cursor()
cur.execute(create)
conn.commit()

with open(IN_TRANSACTION_CSV_LOCATION, 'r') as tx_in_file:
    in_reader = csv.reader(tx_in_file, delimiter=",")
    for row in in_reader:
        if len(row) > 3:
            continue
        tx_hash = row[0]
        wallet_addr = row[1]
        tx_amt = row[2]
        insert_query = "INSERT INTO transfers (tx_hash, wallet_addr, amount, type) VALUES (%s, %s, %s, %s)"
        cur.execute(insert_query, (tx_hash, wallet_addr, tx_amt, "IN"))
        conn.commit()
with open(OUT_TRANSACTION_CSV_LOCATION, 'r') as tx_out_file:
    out_reader = csv.reader(tx_out_file, delimiter=",")
    for row in out_reader:
        if len(row) > 3:
            continue
        tx_hash = row[0]
        wallet_addr = row[1]
        tx_amt = row[2]
        insert_query = "INSERT INTO transfers (tx_hash, wallet_addr, amount, type) VALUES (%s, %s, %s, %s)"
        cur.execute(insert_query, (tx_hash, wallet_addr, tx_amt, "OUT"))
    conn.commit()

conn.close()
