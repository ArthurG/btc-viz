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
MATCH (c:Wallet{address:{addr}})
OPTIONAL MATCH (a:Wallet)-[r1]->(b:Transaction)<-[r2]-(c)
OPTIONAL MATCH (c)-[r3]->(d:Transaction)<-[r4]-(e:Wallet)
return a,r1,b,r2,c,r3,d,r4,e
    """, {"addr": wallet_curious})
    nodes = []
    links = []
    for idx, record in enumerate(result):
  
        if (record["a"] != None):
            node_a = {"id": record["a"].id, "type": "wallet", "group": 1, "address": record["a"]["address"] }
            if (node_a not in nodes):
                nodes.append(node_a)

        if (record["b"] != None):
            node_b = {"id": record["b"].id, "type": "transaction", "group": 2, "hash": record["b"]["hash"] }
            if (node_b not in nodes):
                nodes.append(node_b)

        if (record["c"] != None):
            node_c = {"id": record["c"].id, "type": "wallet", "group": 3, "address": record["c"]["address"] }
            if (node_c not in nodes):
                nodes.append(node_c)

        if (record["d"] != None):
            node_d = {"id": record["d"].id, "type": "transaction", "group": 2, "hash": record["d"]["hash"] }
            if (node_d not in nodes):
                nodes.append(node_d)

        if (record["e"] != None):
            node_e = {"id": record["e"].id, "type": "wallet", "group": 1, "address": record["e"]["address"] }
            if (node_e not in nodes):
                nodes.append(node_e)

        #REverse start/end since r1 is a RECEIVE link
        link_r1 = {"source": record["r1"].end, "target": record["r1"].start, "value": int(record["r1"]["satoshi"])}
        if (link_r1 not in links):
            links.append(link_r1)

        link_r2 = {"source": record["r2"].start, "target": record["r2"].end, "value": int(record["r2"]["satoshi"])}
        if (link_r2 not in links):
            links.append(link_r2)

        link_r3 = {"source": record["r3"].start, "target": record["r3"].end, "value": int(record["r3"]["satoshi"])}
        if (link_r3 not in links):
            links.append(link_r3)

        #REverse start/end since r4 is a RECEIVE link
        link_r4 = {"source": record["r4"].end, "target": record["r4"].start, "value": int(record["r4"]["satoshi"])}
        if (link_r4 not in links):
            links.append(link_r4)



    session.close()
    return json.dumps({"nodes": nodes, "links": links})



if __name__ == "__main__":
    app.run(debug=True)
