import pytest
import specnet as spn
import numpy as np
import scipy as sp

# TODO
class TestFramesSpec:

    @classmethod
    def setup_class(cls):
        cls.G = spn.MagGraph(sym=True)
        cls.G.add_edges_from(
                    [
                        (1,2,{'potential':1}),
                        (1,2),
                        (2,3),
                    ]
                )
        cls.S = [1,3]
        cls.ff = spn.frames.FrameFamily(cls.G, cls.S)

    def test_2frames_isospectrality(self):
        A, B = [1,3],[2,2]
        S1 = [1]
        F13 = self.ff.generate_r_frame(A,S1)
        F22 = self.ff.generate_r_frame(B,S1)

        eigA = np.array(sp.linalg.eigh(
            spn.linalg.laplacian(F13,normalized=True).todense(),
            eigvals_only = True,
        ))
        eigB = np.array(sp.linalg.eigh(
                spn.linalg.laplacian(F22,normalized=True).todense(),
                eigvals_only = True,
        ))

        np.testing.assert_almost_equal(
            np.sort(eigA),
            np.sort(eigB),
            decimal=5,
        )