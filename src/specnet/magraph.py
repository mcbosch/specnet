import networkx as nx

class MagGraph(nx.MultiDiGraph):

    def __init__(self, sym : bool=False, **attr):
        r"""
        Defines a Magnetic Graph as a nx.MultiDiGraph object allowing
        multiple edges and loops. If we set sym as True the graph is going
        to be symmetric. A graph magnetic graph is symmetric if there exists
        an inverse s.t. maps an edge to the inverse direction, with same weight
        and opposite potential.

        If the graph is symmetric, automaticaly is going to add the inverse edges.
        If we add an edge an the inverse, is going to treat them as different edges. 
        
        ```
        >>> import specnet as spn
        >>> M = spn.MagGraph(sym=True)
        >>> M.add_edge(1,2,potential=0.5)
        >>> M.edges(data=True)
        [(1,2,{'potential':0.5}), (2,1,{'potential':-0.5})]
        ```
        Parameters
        ----------
            sym : bool (default=False)
                Defines if the graph is symmetric and we want to automaticaly add
                the inverse edges.
        
            attr : key valued attributes
        
        Returns
        -------
            MagGraph object
        """
        self.sym = sym
        super().__init__(**attr)

    @staticmethod
    def inverse(e):
        r"""
        Returns the inverse direction of an edge. Preserves the weight
        and makes the oposite potential if it exists.

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
    
     
    def add_edge(self, n1, n2, key=None, **attr):
        r"""
        Adding an edge to the graph. If the graph is symmetric the function 
        add two edges. One in each direction with the opposite potential. 
        """

        sym = self.sym
        if sym:            
            k =  super().add_edge(n1, n2, key=key, **attr)
            if 'potential' in attr:
                attr['potential'] = - attr['potential']

            super().add_edge(n2, n1, key=k, **attr)

        else:
            k = super().add_edge(n1, n2, key=key, **attr)
        return k


    def add_edges_from(self, ebunch_to_add, **attr):
        r"""
        The function adds multiple edges to the graph. If the graph is symmetric 
        the function adds both directions with the opposite potential.
        """
        if not self.sym:
            return super().add_edges_from(ebunch_to_add, **attr)
        
        keylist = []
        for e in ebunch_to_add:
            ne = len(e)
            if ne == 4:
                u, v, key, dd = e
            elif ne == 3:
                if isinstance(e[-1], dict):
                    u, v, dd = e
                    key = None
                else:
                    u, v, key = e
                    dd = {}
            elif ne == 2:
                u, v = e
                dd = {}
                key = None
            else:
                msg = f"Edge tuple {e} must be a 2-tuple, 3-tuple or 4-tuple."
                raise ValueError(msg)
            ddd = {}
            ddd.update(attr)
            ddd.update(dd)
            key = self.add_edge(u,v,key)
            self[u][v][key].update(ddd)
            if 'potential' in ddd:
                ddd['potential'] = -ddd['potential']
            self[v][u][key].update(ddd)
            keylist.append(key)
        return keylist
