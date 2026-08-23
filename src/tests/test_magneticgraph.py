import pytest

import networkx as nx
import numpy as np
import specnet as spn

from specnet.magraph import MagGraph


class TestMagneticLaplacian:
    @classmethod
    def setup_class(cls):
        r"""
        We define test for the magnetic laplacian matrix, to check if it correctly
        returns the matrices for an undirected graph and for a directed graph. In the directed
        graph we add edges between nodes in both directions to check that we have a real entry.
        """

        cls.G1 = MagGraph(sym=True)
        cls.G1.add_edges_from((
            (1,2),
            (1,2,{'potential':0.3}),
            (3,2)
        ))


        cls.G2 = MagGraph(sym=True)
        cls.G2.add_edges_from((
            (1,2,{'potential':np.pi}),
            (2,3,{'potential':np.pi}),
            (3,4,{'potential':np.pi}),
            (4,1,{'potential':np.pi})
        ))


        cls.G3 = MagGraph()
        cls.G3.add_edges_from((

        ))

    def test_mag_laplacian(self):

        MG1 = np.array(
            [
                [1, -(1+np.exp(1j * 0.3))/np.sqrt(6), 0],
                [-(1+np.exp(1j * -0.3))/np.sqrt(6), 1, -1/np.sqrt(3)],
                [0, -1/np.sqrt(3), 1],
            ]
        )

        GL = np.array(
            [
                [1, 0.5, 0, 0.5], 
                [0.5, 1, 0.5, 0], 
                [0, 0.5, 1, 0.5], 
                [0.5, 0, 0.5, 1],
            ]
        )

        np.testing.assert_almost_equal(
            spn.linalg.laplacian(self.G1).todense(),
            MG1,
            decimal=3,
        )

        np.testing.assert_almost_equal(
            spn.linalg.laplacian(self.G2).todense(),
            GL,
            decimal=3,
        )