from py2neo import Graph, Path, Node, Relationship
from codecs import open
from json import dumps

fin = open("/media/sf_datasets/accelerate/Belgische Startup Maffia.csv", "r", "latin1")
lines = fin.readlines()[1:]
fin.close()

# post to neo4j
graph = Graph("http://belgian_startup_maffia:FFaPiypFOOS4tRB7pBHl@belgianstartupmaffia.sb02.stations.graphenedb.com:24789/db/data/")
graph.cypher.execute("MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE r,n")

graph.schema.drop_uniqueness_constraint("Company", "name")
graph.schema.drop_uniqueness_constraint("Fund", "name")
graph.schema.drop_uniqueness_constraint("Institute", "name")
graph.schema.drop_uniqueness_constraint("Person", "name")

graph.schema.create_uniqueness_constraint("Company", "name")
graph.schema.create_uniqueness_constraint("Fund", "name")
graph.schema.create_uniqueness_constraint("Institute", "name")
graph.schema.create_uniqueness_constraint("Person", "name")

for line in lines:
  print [line]
  from_type, from_name, edge_type, edge_name, to_type, to_name = line.strip(";\r\n").split(";")

  from_node = graph.merge_one(from_type.strip(), "name", from_name.strip())
  to_node = graph.merge_one(to_type.strip(), "name", to_name.strip())
  from_to = Relationship(from_node, edge_type, to_node)
  graph.create_unique(from_to)

# get nodes with degree
nodes = []
for label in graph.node_labels:
  for p in graph.find(label):
    node = {"id": p.ref.split("/")[-1],
            "label": p["name"], 
            "title": p["name"],
            "value": p.degree,
            "group": label}
    nodes.append(node)
with open("report/nodes.js", "w") as f:
  f.write("var nodesraw = " + dumps(nodes, indent=2) + ";")

# get edges
edges = []
for r in graph.match():
  edge = {"to": r.end_node.ref.split("/")[-1],
          "from": r.start_node.ref.split("/")[-1]
         }
  edges.append(edge)
with open("report/edges.js", "w") as f:
  f.write("var edgesraw = " + dumps(edges, indent=2) + ";")

