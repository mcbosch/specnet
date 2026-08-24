import networkx as nx
import numpy as np

from specnet.magraph import MagGraph

### CONSTRUCTION OF ISOSPECTRAL GRAPHS
class FrameFamily:

    def __init__(self, G : nx.Graph, S : list = []):
        r"""
        Generates a frame family of graphs following the construction
        proposed in [1]. For the construction we need a initial graph
        `G_0` and a subset of vertices `S` which defines the contraction vertices.
        Thus an a frame is a graph consisting a direct sum of a copies `G_0` making 
        the quotient with the nodes S (contracting them).

        Parameters
        ----------
         - G : a MagGraph or NetworkX graph.
         - S : list object. A subset of G.nodes. 

        Returns
        -------
         - A FrameFamily object to treat the family of the frame graphs. 
        
        References
        ----------
        _[1] Fabila-Carrasco, J.S., Lledó, F. & Post, O. 
        A geometric construction of isospectral magnetic graphs. 
        Anal.Math.Phys. 13, 64 (2023).
        <https://doi.org/10.1007/s13324-023-00823-9>
        """

        # Test if the objects are allowed.
        assert isinstance(G, nx.Graph), "Error: introduce a graph object. "
        assert isinstance(S, list), "Error: introduce a list object."

        nodes = G.nodes
        for s in S:
            assert s in nodes, "Elements of S must be nodes"

        # Define initial objects
        self.graph = G
        self.contr_nodes = S


    def generate_frame(self, a : int):
        r"""
        Generation cost O(a·E)
        """
        # Check if there are edges between contracting nodes
        e_in_contr_nodes = []
        for e in self.graph.edges(self.contr_nodes):
            if e[0] in self.contr_nodes and e[1] in self.contr_nodes: e_in_contr_nodes.append(e)

        # Make a MultiGraph if the original graph is not a multigraph and has edges in between contracting nodes.
        if not self.graph.is_multigraph() and len(e_in_contr_nodes) > 0:
            F = nx.MultiDiGraph() if self.graph.is_directed() else nx.MultiGraph()
        else:
            F = type(self.graph)()

        not_sym = F.sym if isinstance(F, MagGraph) else False
        ebunch_to_add = []
        edges = self.graph.edges(data=True) if not_sym else self.graph.edges(data=True, keys=True)
        for i in range(a):
            for e in edges:
                s = e[0] if e[0] in self.contr_nodes else (e[0], i)
                t = e[1] if e[1] in self.contr_nodes else (e[1], i)
                if not_sym:
                    ebunch_to_add.append((s, t, e[-1]))
                else:
                    k = e[2]
                    ebunch_to_add.append((s, t, k, e[-1]))
        F.add_edges_from(ebunch_to_add)
        return F

    def generate_r_frame(self, A : list, S1 : list):
        r"""
        This function generates a graph consisting of a combination of the frame
        graphs with index in A contracted with on the nodes in S1. The nodes of S1
        must be a subset of `self.contr_nodes`. 

        Parameters
        ----------
            - A : a list of integers (>= 1)
            - S1 : a list of nodes in `self.contr_nodes`. 
        
        Returns
        -------
            - F : the contracted frame graph `F_{A, S1}`.
        """
        
        for v in S1: 
            assert v in self.contr_nodes, "S1 must be a subset of the contraction nodes "

        e_in_contr_nodes = []
        for e in self.graph.edges(self.contr_nodes):
            if e[0] in self.contr_nodes and e[1] in self.contr_nodes: e_in_contr_nodes.append(e)
            if e[0] in S1 and e[1] in S1: e_in_contr_nodes.append(e)

        if not self.graph.is_multigraph() and len(e_in_contr_nodes) > 0:
            F = nx.MultiDiGraph() if self.graph.is_directed() else nx.MultiGraph()
        else:
            F = type(self.graph)()


        edges = self.graph.edges(data=True)
        s = len(A)
        for j in range(s):
            a = A[j]
            for i in range(a):
                ebunch_to_add = []
                for e in edges:
                    if e[0] in self.contr_nodes:
                        s = e[0] if e[0] in S1 else (e[0], a, j)
                    else:
                        s = (e[0], i + 1, a, j)

                    if e[1] in self.contr_nodes:
                        t = e[1] if e[1] in S1 else (e[1], a, j)
                    else:
                        t = (e[1], i + 1, a, j)

                    ebunch_to_add.append((s, t, e[-1]))
                F.add_edges_from(ebunch_to_add)

        return F
