import networkx as nx
from specnet.magraph import MagGraph

def laplacian(G, *, 
              nodelist=None, 
              edge_weight="weight", 
              node_weight="weight", 
              normalized=True,
              split_weight=False):
        r"""Returns the magnetic Laplacian matrix of G

        Parameters
        ----------
        nodelist : list, optional (default=list(G))
            Node ordering for row/columns.

        weight : string or None, optional (default='weight')
            Edge attribute key for weights. If None, all edges have weight 1.
        
        normalized : bool, optional (default=True)
            If True returns the normalized version of the Laplacian

        Returns
        -------
        L : SciPy sparse array (complex dtype)
            The magnetic Laplacian matrix of G

        References
        ----------
        ??¿¿
        """
        from collections import defaultdict

        import numpy as np
        import scipy as sp

        if not isinstance(G, MagGraph):
            assert isinstance(G, nx.Graph), f"Expected graph object, introuced {type(G)}."
            if normalized:
                L = nx.linalg.normalized_laplacian_matrix(G, 
                                                          nodelist=nodelist, 
                                                          weight=edge_weight)
            else:
                L = nx.linalg.laplacian_matrix(G, 
                                               nodelist=nodelist, 
                                               weight=edge_weight)
            return L
                 
        if nodelist is None:
            nodelist = list(G)

        # Build Hermitian adjacency H
        n = len(nodelist)
        node_index = {v: i for i, v in enumerate(nodelist)}

        # We compute the relative weights of nodes
        rel_w_nodes = defaultdict(float)
        sw = 0.5 if split_weight else 1

        # Run over out-edges
        for u, v, dd in G.edges(nbunch=nodelist, data=True):
            if G.sym:
                rel_w_nodes[(u)] += dd.get(edge_weight, 1)
            else:
                rel_w_nodes[(u)] += sw * dd.get(edge_weight, 1)
                rel_w_nodes[(v)] += sw * dd.get(edge_weight, 1)
        
        
        rows, cols, data = [], [], defaultdict(complex)
        for u, v, dd in G.edges(data=True):
            if u not in node_index or v not in node_index:
                continue

            ui, vi = node_index[u], node_index[v]

            if (ui, vi) not in data:
                rows.append(ui)
                cols.append(vi)
                if not G.sym:
                    rows.append(vi)
                    cols.append(ui)

            wu, wv = G.nodes[u].get(node_weight, 1), G.nodes[v].get(node_weight, 1)
            norm_term = np.sqrt(rel_w_nodes[u]/wu * rel_w_nodes[v]/wv) if normalized else 1

            if G.sym:
                data[(ui, vi)] += (dd.get(edge_weight, 1) * 
                                   np.exp(1j * dd.get('potential',0)))/norm_term
            else:
                data[(ui, vi)] += sw * (dd.get(edge_weight, 1) * 
                                                   np.exp(1j * dd.get('potential',0)))/norm_term
                data[(vi, ui)] += sw * (dd.get(edge_weight, 1) * 
                                                   np.exp(-1j * dd.get('potential',0)))/norm_term
                
        data_values = list(data.values())
        H = sp.sparse.csr_array((data_values, (rows, cols)), shape=(n, n), dtype=complex)

        # Build degree matrix D
        diags = np.ones(n,) if normalized else np.abs(H).sum(axis=1).ravel() 
        D = sp.sparse.dia_array((diags, 0), shape=(n, n), dtype=complex).tocsr()
        L = D - H
        
        return L