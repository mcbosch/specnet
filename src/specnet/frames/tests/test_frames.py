import pytest

from specnet import MagGraph
from specnet.frames import FrameFamily

# TODO
class TestFrames:

    @classmethod
    def setup_class(cls):
        cls.err_inv_sd = "Error switching directions"
        cls.err_inv_pa = "Error preserving attributes"
        cls.err_inv_op = "Error changing potential"

        cls.G = MagGraph(sym=True)
        cls.G.add_edges_from(
            [
                (1,2,{'potential':1}),
                (1,2),
                (2,3),
            ]
        )
        cls.S = [1,3]
        cls.ff = FrameFamily(cls.G, cls.S)

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

        u1, v1, k1, d1 = TestFrames.get_edge_attr(e1)
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

    def test_frame_construction(self):
        a = 3
        F = self.ff.generate_frame(a)
        desired_edges = [
            (1,(2,0),0,{'potential':1}),
            (1,(2,1),0,{'potential':1}),
            (1,(2,2),0,{'potential':1}),
            (1,(2,0),1,{}),
            (1,(2,1),1,{}),
            (1,(2,2),1,{}),
            ((2,0),3,0,{}),
            ((2,1),3,0,{}),
            ((2,2),3,0,{}),
        ]

        for e in desired_edges:
            u, v, k, d = e
            assert TestFrames.assert_edge_in_adj(F,u,v,k,d,inverse=True)
        
    def test_2frames_join(self):
        A = [1,3]
        S1 = [1]
        F = self.ff.generate_r_frame(A,S1)
        desired_edges = [
            (1, (2,0,0), 0, {'potential':1}),
            (1, (2,0,0), 1, {}),
            ((2,0,0), (3,0), 0, {}),
            (1, (2,0,1), 0, {'potential':1}),
            (1, (2,1,1), 0, {'potential':1}),
            (1, (2,2,1), 0, {'potential':1}),
            (1, (2,0,1), 1, {}),
            (1, (2,1,1), 1, {}),
            (1, (2,2,1), 1, {}),
            ((2,0,1), (3,1), 0, {}),
            ((2,1,1), (3,1), 0, {}),
            ((2,2,1), (3,1), 0, {}),
        ]

        for e in desired_edges:
            u, v, k, d = e
            assert TestFrames.assert_edge_in_adj(F, u, v, k, d, inverse=True)

    def test_3frames_join(self):
        A = [1,1,3]
        S1 = [1]
        F = self.ff.generate_r_frame(A,S1)
        desired_edges = [
            (1, (2,0,0), 0, {'potential':1}),
            (1, (2,0,0), 1, {}),
            ((2,0,0), (3,0), 0, {}),
            (1, (2,0,1), 0, {'potential':1}),
            (1, (2,0,1), 1, {}),
            ((2,0,1), (3,1), 0, {}),
            (1, (2,0,2), 0, {'potential':1}),
            (1, (2,1,2), 0, {'potential':1}),
            (1, (2,2,2), 0, {'potential':1}),
            (1, (2,0,2), 1, {}),
            (1, (2,1,2), 1, {}),
            (1, (2,2,2), 1, {}),
            ((2,0,2), (3,2), 0, {}),
            ((2,1,2), (3,2), 0, {}),
            ((2,2,2), (3,2), 0, {}),
        ]

        for e in desired_edges:
            u, v, k, d = e
            assert TestFrames.assert_edge_in_adj(F, u, v, k, d, inverse=True)
