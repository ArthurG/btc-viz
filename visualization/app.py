from flask import Flask, render_template, request

from neo4j.v1 import GraphDatabase, basic_auth
import json
import math

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/get_neighbour_wallet")
def get_json():
    wallet_curious = request.args.get("wallet")
    print(wallet_curious)

    driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "123123"))
    session = driver.session()
    result = session.run("""
    MATCH (a:Wallet)-[r1]->(b:Transaction)<-[r2]-(c:Wallet {address:{addr}})-[r3]->(d:Transaction)<-[r4]-(e)
    WHERE a <> c AND c<>e AND a<> e
    return a,r1,b,r2,c,r3,d,r4,e LIMIT 100
    """, {"addr": wallet_curious})
    nodes = []
    links = []
    for idx, record in enumerate(result):

        node_a = {"id": record["a"].id, "type": "wallet", "group": 1, "address": record["a"]["address"] }
        node_b = {"id": record["b"].id, "type": "transaction", "group": 2, "hash": record["b"]["hash"] }
        node_c = {"id": record["c"].id, "type": "wallet", "group": 1, "address": record["c"]["address"] }
        node_d = {"id": record["d"].id, "type": "transaction", "group": 2, "hash": record["d"]["hash"] }
        node_e = {"id": record["e"].id, "type": "wallet", "group": 1, "address": record["e"]["address"] }
        if (node_a not in nodes):
            nodes.append(node_a)
        if (node_b not in nodes):
            nodes.append(node_b)
        if (node_c not in nodes):
            nodes.append(node_c)
        if (node_d not in nodes):
            nodes.append(node_d)
        if (node_e not in nodes):
            nodes.append(node_e)

        link_r1 = {"source": node_a["id"], "target": node_b["id"], "value": math.log(int(record["r1"]["satoshi"]))}
        link_r2 = {"source": node_b["id"], "target": node_c["id"], "value": math.log(int(record["r2"]["satoshi"]))}
        link_r3 = {"source": node_c["id"], "target": node_d["id"], "value": math.log(int(record["r3"]["satoshi"]))}
        link_r4 = {"source": node_d["id"], "target": node_e["id"], "value": math.log(int(record["r4"]["satoshi"]))}
        links.extend([link_r1, link_r2, link_r3, link_r4])
 
    session.close()
    return json.dumps({"nodes": nodes, "links": links})



if __name__ == "__main__":
    app.run()
