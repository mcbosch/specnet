import networkx as nx

class MagGraph(nx.MultiDiGraph):

    def __init__(self, **attr):
        r"""
        Defines a Magnetic Graph as a nx.MultiDiGraph object allowing
        multiple edges and loops. Some modifications are done in order

        WARNING: MAGNETIC GRAPHS ARE SYMMETRIC. WE SHOULD ADD A PARAMETER
        TO SPLIT ONLY ONE DIRECTIONAL EDGES. 
        """
        super().__init__(**attr)

    @staticmethod
    def opposite(e):
        r"""
        Returns the opposite direction of an edge.

        Parameters
        ----------
            e : An edge (tuple of len >= 2)

        Raise
        -----
            Error if e is not an edge
        """
        assert len(e)>=2, "Error: only edges allowed (len>=2)"

        if isinstance(e[-1], dict):
            e2d = e[-1].copy()
            if 'potential' in e2d:
                e2d['potential'] = - e2d['potential']
            e2 = (e[1], e[0]) + e[2:-1] + (e2d,)
        else:
            e2 = (e[1], e[0]) + e[2:]

        return e2 
    
     
    def add_edge(self, n1, n2, key=None, sym=False, split_weight=False, weight="weight", **attr):
        r"""
        Adding an edge to the graph. If the graph is symmetric the function 
        add two edges. One in each direction with the opposite potential. 
        """
        
        if sym:
            if split_weight:
                attr[weight] = 0.5 * attr.get(weight, 1)
            
            k =  super().add_edge(n1, n2, key=key, **attr)

            if 'potential' in attr:
                attr['potential'] = - attr['potential']
            super().add_edge(n2, n1, key=k, **attr)

        else:
            k = super().add_edge(n1, n2, key=key, **attr)
        return k


    def add_edges_from(self, ebunch_to_add, sym=True, weight='weight', split_weight=False, **attr):
        r"""
        The function adds multiple edges to the graph. If the graph is symmetric 
        the function adds both directions with the opposite potential.
        """

        if not sym:
            return super().add_edges_from(ebunch_to_add, **attr)

        ebunch = []

        for e in ebunch_to_add:
            if sym:
                if split_weight:
                    dd = e[-1]

                    if not isinstance(dd, dict):
                        dd = {}
                        e = e + (dd,)

                    if isinstance(weight, str):
                        w = dd.get(weight, 1) if weight in dd else attr.get(weight, 1)
                        key = weight
                    else:
                        w = dd.get('weight', weight)
                        key = 'weight'
                    dd[key] = 0.5 * w

                ebunch.append(e)
                ebunch.append(self.opposite(e))

        return super().add_edges_from(ebunch, **attr)

    #TODO
    def add_symmetries(self, weight='weight', split_weight=False):
        r"""
        Checks that all edges are symmetric and adds edges if necessary
        """
        from collections import defaultdict

        symm = defaultdict(float)
        for u, v, k in self.edges(keys=True):
            symm[(u, v, k)] += 1
            symm[(v, u, k)] -= 1

        v = symm.values()
        for i in v:
            if i != 0:
                return False
        return True

    #TODO
    def check_symmetries(self) -> bool:
        pass


    def laplacian(self, *, nodelist=None, edge_weight="weight", node_weight="weight", normalized=True):
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

        if nodelist is None:
            nodelist = list(self)

        # Build Hermitian adjacency H
        n = len(nodelist)
        node_index = {v: i for i, v in enumerate(nodelist)}

        # We compute the relative weights of nodes
        rel_w_nodes = defaultdict(float)

        # Run over out-edges
        for u, _, dd in self.edges(nbunch=nodelist, data=True):
            rel_w_nodes[(u)] += dd.get(edge_weight, 1)
        
        
        rows, cols, data = [], [], defaultdict(complex)
        for u, v, dd in self.edges(data=True):
            if u not in node_index or v not in node_index:
                continue

            ui, vi = node_index[u], node_index[v]

            if (ui, vi) not in data:
                rows.append(ui)
                cols.append(vi)

            wu, wv = self.nodes[u].get(node_weight, 1), self.nodes[v].get(node_weight, 1)
            norm_term = np.sqrt(rel_w_nodes[u]/wu * rel_w_nodes[v]/wv) if normalized else 1
            data[(ui, vi)] += (dd.get(edge_weight, 1) * 
                                   np.exp(1j * dd.get('potential',0)))/norm_term

        data_values = list(data.values())
        H = sp.sparse.csr_array((data_values, (rows, cols)), shape=(n, n), dtype=complex)

        # Build degree matrix D
        diags = np.ones(n,) if normalized else np.abs(H).sum(axis=1).ravel() 
        D = sp.sparse.dia_array((diags, 0), shape=(n, n), dtype=complex).tocsr()
        L = D - H
        
        return L

    def spectra(self, *, nodelist=None, weight="weight", normalized=True, eigenfunctions=False):
        r"""
        Computes the spectra of the magnetic laplacian. If the matrix is hermitic.
        """

        import scipy as sp

        # Check if the matrix is hermitic
        # TODO

        L = self.laplacian(nodelist=nodelist, weight=weight, normalized=normalized)
        return sp.linalg.eigh(
                L.todense(),
                eigvals_only=not eigenfunctions,
            )

    def symb_laplacian(self, *, nodelist=None, weight="weight", normalized=True, potential={}):
        pass

    
