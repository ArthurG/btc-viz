from constants import *
import csv

walletsMap={} #address -> number OR transaction_id->number
lastNumber = 0

with open(IN_TRANSACTION_CSV_LOCATION, 'r') as tx_in_file:
    in_reader = csv.reader(tx_in_file, delimiter=",")
    for row in in_reader:
        tx_hash = row[0]
        wallet_addr = row[1]
        tx_amt = row[2]
        
        if wallet_addr in walletsMap:
            wallet_id = walletsMap[wallet_addr]
        else:
            wallet_id = lastNumber
            walletsMap[wallet_addr] = wallet_id
            lastNumber+=1

        if tx_hash in walletsMap:
            tx_id = walletsMap[tx_hash]
        else:
            tx_id = lastNumber
            walletsMap[tx_hash] = tx_id
            lastNumber+=1

        print("CREATE ("+str(wallet_id)+":Wallet {address: \""+wallet_addr+"\"})-[:SENT {satoshi: \""+str(tx_amt)+"\"}]->("+str(tx_id)+":Tx {hash:\""+tx_hash+"\"});")

with open(OUT_TRANSACTION_CSV_LOCATION, 'r') as tx_out_file:
    out_reader = csv.reader(tx_out_file, delimiter=",")
    for row in out_reader:
        tx_hash = row[0]
        wallet_addr = row[1]
        tx_amt = row[2]
        
        if wallet_addr in walletsMap:
            wallet_id = walletsMap[wallet_addr]
        else:
            wallet_id = lastNumber
            walletsMap[wallet_addr] = wallet_id
            lastNumber+=1

        if tx_hash in walletsMap:
            tx_id = walletsMap[tx_hash]
        else:
            tx_id = lastNumber
            walletsMap[tx_hash] = tx_id
            lastNumber+=1


        print("CREATE ("+str(wallet_id)+":Wallet {address: \""+wallet_addr+"\"})-[:RECEIVED {satoshi: \""+str(tx_amt)+"\"}]->("+str(tx_id)+":Tx {hash:\""+tx_hash+"\"});")
