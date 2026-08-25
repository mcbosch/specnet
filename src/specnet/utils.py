from specnet.magraph import MagGraph
from networkx import Graph

import json
import os
import sys

def read_graph(path, typeg) -> MagGraph:
    with open(f"{path}", "r") as f:
        adj = json.load(f)

    G = typeg()
    G._adj = adj
    return G    

def save_graph(G : MagGraph=None, path : str=None, name : str = None) -> str:

    if not isinstance(G, Graph) : raise ValueError(f"{type(G)} should be a graph object")
    if path is None: raise ValueError("Introduce a path where save the graph")

    if G.is_multigraph():
        ebunch = G.edges(data=True, keys=True)
    else:
        ebunch = G.edges(data=True)

    with open(f"{path}/{name}.json", "w") as f:
        json.dump(G._adj, f, indent=4)

    return f"{path}/{name}"