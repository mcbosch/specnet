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


        cls.G3 = MagGraph(sym=False)
        cls.G3.add_edges_from((
            (1,2,{'potential':1}),
            (1,2,{'weight':2, 'potential':0.5}),
            (2,1,{'weight':4, 'potential':1}),
            (1,3),
            (2,4)
        ))

    def test_mag_laplacian_sym(self):

        MG1 = np.array(
            [
                [1, -(1+np.exp(1j * 0.3))/np.sqrt(6), 0],
                [-(1+np.exp(1j * -0.3))/np.sqrt(6), 1, -1/np.sqrt(3)],
                [0, -1/np.sqrt(3), 1],
            ]
        )

        MG1_not_normalise = np.array(
            [
                [2, -(1+np.exp(1j * 0.3)), 0],
                [-(1+np.exp(1j * -0.3)), 3, -1],
                [0, -1, 1],
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

        GL_not_normalised = np.array(
            [
                [2, 1, 0, 1], 
                [1, 2, 1, 0], 
                [0, 1, 2, 1], 
                [1, 0, 1, 2],
            ]
        )


        np.testing.assert_almost_equal(
            spn.linalg.laplacian(self.G1).todense(),
            MG1,
            decimal=5,
        )

        np.testing.assert_almost_equal(
            spn.linalg.laplacian(self.G1, normalized=False).todense(),
            MG1_not_normalise,
            decimal=5,
        )
        
        np.testing.assert_almost_equal(
            spn.linalg.laplacian(self.G2).todense(),
            GL,
            decimal=5,
        )

        np.testing.assert_almost_equal(
            spn.linalg.laplacian(self.G2, normalized=False).todense(),
            GL_not_normalised,
            decimal=5,
        )


    def test_mag_laplacian_nsym(self):


        MG3_W_not_normalised = np.array(
            [
                [8, -(np.exp(1j)+2*np.exp(0.5j)+4*np.exp(-1j)), -1, 0],
                [-(np.exp(-1j)+2*np.exp(-0.5j)+4*np.exp(1j)), 8, 0, -1],
                [-1, 0, 1, 0],
                [0, -1, 0, 1],
            ]
        )

        MG3_W_normalised = np.array(
            [
                [1, -(np.exp(1j)+2*np.exp(0.5j)+4*np.exp(-1j))/8, -1/np.sqrt(8), 0],
                [-(np.exp(-1j)+2*np.exp(-0.5j)+4*np.exp(1j))/8, 1, 0, -1/np.sqrt(8)],
                [-1/np.sqrt(8), 0, 1, 0],
                [0, -1/np.sqrt(8), 0, 1],
            ]
        )
        
        MG3_weight_split_not_normalised = np.array(
            [
                [4, -(0.5*np.exp(1j)+np.exp(0.5j)+2*np.exp(-1j)), -0.5, 0],
                [-(0.5*np.exp(-1j)+np.exp(-0.5j)+2*np.exp(1j)), 4, 0, -0.5],
                [-0.5, 0, 0.5, 0],
                [0, -0.5, 0, 0.5],
            ]
        )

        MG3_weight_split_normalised = np.array(
            [
                [1, -(0.5*np.exp(1j)+np.exp(0.5j)+2*np.exp(-1j))/4, -0.5/(2*np.sqrt(0.5)), 0],
                [-(0.5*np.exp(-1j)+np.exp(-0.5j)+2*np.exp(1j))/4, 1, 0, -0.5/(2*np.sqrt(0.5))],
                [-0.5/(2*np.sqrt(0.5)), 0, 1, 0],
                [0, -0.5/(2*np.sqrt(0.5)), 0, 1],
            ]
        )

        np.testing.assert_almost_equal(
                        spn.linalg.laplacian(self.G3, normalized=False).todense(),
                        MG3_W_not_normalised,
                        decimal=5,
                    )

        np.testing.assert_almost_equal(
                        spn.linalg.laplacian(self.G3, normalized=True).todense(),
                        MG3_W_normalised,
                        decimal=5,
                    )

        np.testing.assert_almost_equal(
                        spn.linalg.laplacian(self.G3, normalized=False, split_weight=True).todense(),
                        MG3_weight_split_not_normalised,
                        decimal=5,
                    )

        np.testing.assert_almost_equal(
                        spn.linalg.laplacian(self.G3, normalized=True, split_weight=True).todense(),
                        MG3_weight_split_normalised,
                        decimal=5,
                    )