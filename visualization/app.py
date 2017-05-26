from flask import Flask, render_template

from neo4j.v1 import GraphDatabase, basic_auth
import json
import math

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/miserables.json")
def get_json():

    driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "123123"))
    session = driver.session()
    result = session.run("""
    MATCH (a:Wallet)-[r1]->(b:Transaction)<-[r2]-(c:Wallet {address:'12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S'})-[r3]->(d:Transaction)<-[r4]-(e)
    WHERE a <> c AND c<>e AND a<> e
    return a,r1,b,r2,c,r3,d,r4,e LIMIT 100
    """)
    nodes = []
    links = []
    for idx, record in enumerate(result):

        node_a = {"id": str(idx) + "a" + str(record["a"].id), "type": "wallet", "group": 1, "address": record["a"]["address"] }
        node_b = {"id": str(idx) + "b" + str(record["b"].id), "type": "transaction", "group": 2, "hash": record["b"]["hash"] }
        node_c = {"id": str(record["c"].id), "type": "wallet", "group": 1, "address": record["c"]["address"] }
        node_d = {"id": str(idx) + "d" + str(record["d"].id), "type": "transaction", "group": 2, "hash": record["d"]["hash"] }
        node_e = {"id": str(idx) + "e" + str(record["e"].id), "type": "wallet", "group": 1, "address": record["e"]["address"] }
        nodes.extend([node_a, node_b, node_c, node_d, node_e])

        link_r1 = {"source": str(idx) + "a" + str(record["a"].id), "target": str(idx) + "b" + str(record["b"].id), "value": math.log(int(record["r1"]["satoshi"]))}
        link_r2 = {"source": str(idx) + "b" + str(record["b"].id), "target": str(record["c"].id), "value": math.log(int(record["r2"]["satoshi"]))}
        link_r3 = {"source": str(record["c"].id), "target": str(idx) + "d" + str(record["d"].id), "value": math.log(int(record["r3"]["satoshi"]))}
        link_r4 = {"source": str(idx) + "d" + str(record["d"].id), "target": str(idx) + "e" + str(record["e"].id), "value": math.log(int(record["r4"]["satoshi"]))}
        links.extend([link_r1, link_r2, link_r3, link_r4])
    session.close()
    print(len(nodes))

    return json.dumps({"nodes": nodes, "links": links})



if __name__ == "__main__":
    app.run()
