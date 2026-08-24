import networkx as nx
from specnet.magraph import MagGraph

def laplacian(G, *, 
              nodelist=None, 
              edge_weight="weight", 
              node_weight="weight", 
              normalized=True,
              split_weight=False):
        r"""Returns the magnetic Laplacian matrix of G. The magnetic
        Laplacian is a graph operator where there is a potential vector
        acting on the graph. That is a function 
        :math:`\alpha:\ell^2(E)\rightarrow \mathbb{R}/2\pi\mathbb{Z}.`
        
        The magnetic laplacian is the second order derivate of a function in
        :math:`\ell^2(V)`. That is :math:`d_{\alpha}^*d_{\alpha}` where 
        :math:`d_{\alpha}` is the twisted derivate:

        ::math::```
        (d_{\alpha}f)(e) = e^{i\alpha(e)/2}f(\partial_+e) - 
                                      e^{-i\alpha(e)/2}f(\partial_-e)  
        ```

        For a MagGraph G if it is not symmetric we use the definition
        used in [2]. If the parameter split_weight is True, the edge weight
        is going to be divided by two. If the graph is symmetric we use the 
        definition from [1]. For a further explanation on how these definitions
        are obtained and how they relate we leave the calculations in [3].

        Parameters
        ----------
        G : nx.Graph
            Graph, can be any kind of nx.Graph or MagGraph.

        nodelist : list, optional (default=list(G))
            Node ordering for row/columns.

        weight : string or None, optional (default='weight')
            Edge attribute key for weights. If None, all edges have weight 1.
        
        normalized : bool, optional (default=True)
            If True returns the normalized version of the Laplacian
        
        split_weight : bool, optional ()

        Returns
        -------
        L : SciPy sparse array (complex dtype)
            The magnetic Laplacian matrix of G

        References
        ----------
        _[1] Fabila-Carrasco, J.S., Lledó, F. & Post, O. 
        A geometric construction of isospectral magnetic graphs. 
        Anal.Math.Phys. 13, 64 (2023).
        <https://doi.org/10.1007/s13324-023-00823-9>

        _[2] Fabila-Carrasco, J.S., Lledó, F., Post, O.: 
        Spectral gaps and discrete magnetic Laplacians. 
        Linear Algebra Appl. 547, 183–216 (2018).
        <https://www.sciencedirect.com/science/article/pii/S0024379518300673>

        _[3] Melcion Ciudad Bosch: Calculations
        <https://mcbosch.github.io/documentations/specnet/magnetic-laplacian-def.pdf>
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
            ui, vi = node_index[u], node_index[v]
            if G.sym:
                rel_w_nodes[(ui)] += dd.get(edge_weight, 1)
            else:
                rel_w_nodes[(ui)] += sw * dd.get(edge_weight, 1)
                rel_w_nodes[(vi)] += sw * dd.get(edge_weight, 1)
        
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
            norm_term = np.sqrt(rel_w_nodes[ui]/wu * rel_w_nodes[vi]/wv) if normalized else 1

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
        diags = np.ones(n,) if normalized else np.array([rel_w_nodes[i] for i in range(n)])
        D = sp.sparse.dia_array((diags, 0), shape=(n, n), dtype=complex).tocsr()
        L = D - H
        
        return L