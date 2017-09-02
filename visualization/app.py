from flask import Flask, render_template, request, send_from_directory

from neo4j.v1 import GraphDatabase, basic_auth
import json
import math
import requests

app = Flask(__name__)

@app.route("/")
def main():
    return send_from_directory('static/html', 'index.html')

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)

def get_neo(wallet_curious):
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
                nodes.insert(0, node_c) #Need to insert root wallet at index 0

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

def get_graphflow(wallet_curious):
    endpoint = "http://localhost:8000/query"

    #Get the things the wallet has received
    ids = set()
    nodes = []
    links = []

    query = "MATCH (a {address:\""+wallet_curious+"\"})-[:RECEIVED]->(b), (c)-[:SENT]->(b);"
    resp = requests.post(endpoint, query)
    res = resp.json()
    for vertex in res["vertices"]:
        v = res["vertices"][vertex]
        ids.add(v["id"])
        if(v["type"] == "Tx"):
            nodes.append({"id": v["id"], "type": "transaction", "group": "2", "hash": v["properties"]["hash"]})
        elif v["properties"]["address"] == wallet_curious:
            nodes.append({"id": v["id"], "type": "wallet", "group": "1", "address": v["properties"]["address"]})
        else:
            nodes.append({"id": v["id"], "type": "wallet", "group": "3", "address": v["properties"]["address"]})
    for edge in res["edges"]:
        e = res["edges"][edge]
        if e["type"] == "RECEIVED":
            links.append({"source": res["vertices"][str(e["to_vertex_id"])]["id"], "target": e["from_vertex_id"], "value": int(e["properties"]["satoshi"])})
        else:
            links.append({"source": res["vertices"][str(e["from_vertex_id"])]["id"],"target": e["to_vertex_id"], "value": int(e["properties"]["satoshi"])})

    query = "MATCH (a {address:\""+wallet_curious+"\"})-[:SENT]->(b), (c)-[:RECEIVED]->(b);"
    resp = requests.post(endpoint, query)
    res = resp.json()
    for vertex in res["vertices"]:
        v = res["vertices"][vertex]
        if(v["id"] in ids):
            continue
         
        ids.add(v["id"])
        if(v["type"] == "Tx"):
            nodes.append({"id": v["id"], "type": "transaction", "group": "2", "hash": v["properties"]["hash"]})
        elif v["properties"]["address"] == wallet_curious:
            nodes.append({"id": v["id"], "type": "wallet", "group": "1", "address": v["properties"]["address"]})
        else:
            nodes.append({"id": v["id"], "type": "wallet", "group": "3", "address": v["properties"]["address"]})

    for edge in res["edges"]:
        e = res["edges"][edge]
        if e["type"] == "RECEIVED":
            links.append({"source": res["vertices"][str(e["to_vertex_id"])]["id"], "target": e["from_vertex_id"], "value": int(e["properties"]["satoshi"])})
        else:
            links.append({"source": res["vertices"][str(e["from_vertex_id"])]["id"], "target": e["to_vertex_id"], "value": int(e["properties"]["satoshi"])})

    return json.dumps({"nodes": nodes, "links": links})


@app.route("/get_neighbour_wallet")
def get_json():
    wallet_curious = request.args.get("wallet")
    return get_graphflow(wallet_curious)
    #return get_neo(wallet_curious)

    
@app.route("/get_entity")
def get_entity():
    entity_curious = request.args.get("entity")
    ans = set()
    new = set([entity_curious])
    endpoint = "http://localhost:8000/query"
    while (len(new) > 0):
        ans.update(new)
        new2 = set()

        for wallet_curious in new:
            query = "MATCH (a {address:\""+wallet_curious+"\"})-[:RECEIVED]->(b), (c)-[:RECEIVED]->(b);"
            resp = requests.post(endpoint, query)
            newJson = resp.json()
            for nodeId in newJson["vertices"]:
                if newJson["vertices"][nodeId]["type"] == "Wallet" and newJson["vertices"][nodeId]["properties"]["address"] not in ans.union(new).union(new2):
                    new2.add(newJson["vertices"][nodeId]["properties"]["address"])

            query = "MATCH (a {address:\""+wallet_curious+"\"})-[:SENT]->(b), (c)-[:SENT]->(b);"
            resp = requests.post(endpoint, query)
            newJson = resp.json()
            for nodeId in newJson["vertices"]:
                if newJson["vertices"][nodeId]["type"] == "Wallet" and newJson["vertices"][nodeId]["properties"]["address"] not in ans.union(new).union(new2):
                    new2.add(newJson["vertices"][nodeId]["properties"]["address"])
        new = new2
    return json.dumps(list(ans))




if __name__ == "__main__":
    app.run(debug=True)
