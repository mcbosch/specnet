import networkx as nx

class MagGraph(nx.MultiDiGraph):

    def __init__(self, sym : bool=False, **attr):
        r"""
        Defines a Magnetic Graph as a nx.MultiDiGraph object allowing
        multiple edges and loops. Some modifications are done in order

        WARNING: MAGNETIC GRAPHS ARE SYMMETRIC. WE SHOULD ADD A PARAMETER
        TO SPLIT ONLY ONE DIRECTIONAL EDGES. 
        """
        self.sym = sym
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
