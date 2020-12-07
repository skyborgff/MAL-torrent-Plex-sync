import networkx as nx
import os
from networkx.readwrite import json_graph
import json
import pickle
import jsonpickle

database_folder = f'Settings/Database'
database_file = f'graph.gpickle'
database_path = os.path.join(database_folder, database_file)


class Database:
    def __init__(self):
        self.graph: nx.classes.Graph = None
        self.load_graph()


    def load_graph(self):
        os.makedirs(database_folder, exist_ok=True)
        if os.path.exists(database_path):
            self.graph = nx.read_gpickle(database_path)
        else:
            self.graph = nx.DiGraph()

    def save(self):
        nx.write_gpickle(self.graph, database_path)

    def generate_graph(self, path):
        d = json_graph.node_link_data(self.graph)
        data = jsonpickle.encode(d, unpicklable=True, indent=1)
        with open(path, "w+") as file:
            file.write(data)
        print(f"Wrote node-link JSON data to {path}")

# Note To Self: Pickling stuff for the graph