from specnet.magraph import MagGraph

import json
import os
import sys

def _cache_clear():
    pass

def read_graph(path) -> MagGraph:
    pass

def save_graph(G : MagGraph=None, path : str=None) -> str:
    r"""
    
    """
    if G is None: raise ValueError
    if path is None: raise ValueError

    ebunch = G.edges(data=True, keys=True)
    