from flask import Flask, render_template

from neo4j.v1 import GraphDatabase, basic_auth

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.btml')

@app.route("/miserables.json")
def get_json():

    driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "123123"))
    session = driver.session()
    result = session.run("""
    MATCH (a:Wallet)-[r1]->(b:Transaction)<-[r2]-(c:Wallet)-[r3]->(d:Transaction)<-[r4]-(e)
    WHERE a <> c AND c<>e AND a<> e
    return a,r1,b,r2,c,r3,d,r4,e LIMIT 100
    """)
    nodes = []
    links = []
    for idx, record in enumerate(result):

        node_a = {"id": str(idx) + "a" + str(record["a"].id), "type": "wallet", "group": 1, "address": record["a"]["address"] }
        node_b = {"id": str(idx) + "b" + str(record["b"].id), "type": "wallet", "group": 1, "address": record["b"]["address"] }
        node_c = {"id": str(idx) + "c" + str(record["c"].id), "type": "wallet", "group": 1, "address": record["c"]["address"] }
        node_d = {"id": str(idx) + "d" + str(record["d"].id), "type": "wallet", "group": 1, "address": record["d"]["address"] }
        node_e = {"id": str(idx) + "e" + str(record["e"].id), "type": "wallet", "group": 1, "address": record["e"]["address"] }
        nodes.extend([node_a, node_b, node_c, node_d, node_e])

        link_r1 = {"source": 

    session.close()



    return render_template('miserables.json')



if __name__ == "__main__":
    app.run()
