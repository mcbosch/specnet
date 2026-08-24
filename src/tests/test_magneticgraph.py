import pytest

import networkx as nx
import numpy as np
import specnet as spn

from specnet.magraph import MagGraph


class TestMagGraph:
    @classmethod
    def setup_class(cls):
         r"""
         Define possible errors.
         """
         # Errors related with the inversion of an edge
         cls.err_inv_sd = "Error switching directions"
         cls.err_inv_pa = "Error preserving attributes"
         cls.err_inv_op = "Error changing potential"

    @staticmethod
    def get_edge_attr(e):
        ne = len(e)
        if ne == 4:
            u, v, k, d = e
        elif ne == 3:
            if isinstance(e[-1], dict):
                u, v, d = e
                k = None
            else:
                u, v, k = e
                d = None
        elif ne == 2:
            u, v = e
            k, d = None, None
        else:
            raise ValueError(f"Edges must be 2-tuple, 3-tuple or 4-tuple")
        
        return u, v, k, d

    @staticmethod
    def assert_edge_in_adj(G, u, v, k, d, inverse=False):
        r"""
        Verifies if an edge is in _adj as expected. If inverse=True
        checks for that edge and the inverse one.
        """

        assert v in G._adj[u], "Connection error"
        assert k in G._adj[u][v], "Key error"
        if inverse:
            assert u in G._adj[v], "Connection error"
            assert k in G._adj[v][u], "Key error"

        dict_keys = d.keys()
        dd = G[u][v][k]
        assert len(d) == len(dd), "Not the same dict as expected"
        for dk in dict_keys:
            msg = "Attributes are not the same as expected"
            assert dk in dd and dd[dk] == d[dk], msg
            if inverse:
                if dk == 'potential':
                    assert dk in G._adj[v][u][k] and G._adj[v][u][k][dk] == -d[dk], msg
                else:
                    assert dk in G._adj[v][u][k] and G._adj[v][u][k][dk] == d[dk], msg

        return True

    
    def compare_edges(self, e1, e2, inverted=False):
        n1, n2 = len(e1), len(e2)
        assert n1==n2, f"The edges {e1} and {e2} are not of the same length"

        u1, v1, k1, d1 = TestMagGraph.get_edge_attr(e1)
        u2, v2, k2, d2 = self.get_edge_attr(e2)

        if inverted:
            assert u1 == v2 and v1 == u2, self.err_inv_sd
        else:
            assert u1 == u2 and v1 == v2, "Edges are not the same"
        assert k1 == k2, "Edges don't have the same key"
        if d1 == None or d2 == None:
            assert d1 == d2
        keys = d1.keys()
        err_msg = "Edges have different attributes"
        for k in keys:
            assert k in d2, err_msg
            if k=='potential' and inverted:
                assert d1[k]==-d2[k], "The potential is not inverted"
            else:
                assert d1[k] == d2[k], err_msg

        return True
         
    def test_inverse(self):
        e = (1,2,0,{'w':2, 'potential':1})
        ei = MagGraph.inverse(e)

        assert self.compare_edges(e, ei, inverted=True)
        
    def test_add_edge(self):
        # Would be great to check the edges in G._adj and not in G.edges
        G = MagGraph(sym=True)
        H = MagGraph(sym=False)
        e = (1,2,1,{'weight':2, 'potential':1})

        G.add_edge(1,2,1,weight = 2, potential = 1)
        H.add_edge(1,2,1,weight = 2, potential = 1)

        edges_G = list(G.edges(data=True, keys=True))
        edges_H = list(H.edges(data=True, keys=True))

        assert len(edges_G) == 2, "G should have 2 edges"
        assert len(edges_H) == 1, "H should have 1 edge"

        assert self.compare_edges(edges_G[0], e, inverted=False)
        assert self.compare_edges(edges_H[0], e, inverted=False)

        assert self.compare_edges(edges_G[0], edges_G[1], inverted=True)

    def test_add_edges_from(self):
        e1 = (1,2,{'weight':2, 'potential':1})
        e2 = (1,2,2)
        e3 = (2,3,1,{'potential':-1})
        ebunch = [e1, e2, e3]

        G = MagGraph(sym=True)
        H = MagGraph(sym=False)

        G.add_edges_from(ebunch)
        H.add_edges_from(ebunch)

        assert len(G.edges()) == 2 * len(ebunch)
        assert len(H.edges()) == len(ebunch)

        assert self.assert_edge_in_adj(G, e1[0], e1[1], 0, e1[-1], inverse=True)
        assert self.assert_edge_in_adj(G, e2[0], e2[1], 2, {}, inverse=True)
        assert self.assert_edge_in_adj(G, e3[0], e3[1], 1, e3[-1], inverse=True)

        assert self.assert_edge_in_adj(H, e1[0], e1[1], 0, e1[-1], inverse=False)
        assert self.assert_edge_in_adj(H, e2[0], e2[1], 2, {}, inverse=False)
        assert self.assert_edge_in_adj(H, e3[0], e3[1], 1, e3[-1], inverse=False)

        

        