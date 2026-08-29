from specnet.magraph import MagGraph
from specnet.frames.frame_graphs import FrameFamily
from networkx.drawing.layout import spring_layout

import matplotlib.pyplot as plt
import numpy as np

def _arc(p0, p1, theta, k = 100):
    r"""
    This functions returns a (k, 2)-array
    with the points defining an arc that gpes 
    from p0 to p1 with incidence angle theta.
    """
    # Define unit vector with direction p0->p1
    v = np.array(
        [p1[0]-p0[0], p1[1]-p0[1]]
    )
    l = np.sqrt(v[0]**2 + v[1]**2)
    v = v/l
    # Define perpendicular vector from v
    u = np.array([-v[1],v[0]])
    # Use u and v as a base
    t = np.linspace(0,l,k)
    h = np.tan(theta)*np.sin(np.pi/l * t)
    vt = t.reshape(-1,1) * v 
    uh = h.reshape(-1,1) * u

    return p0 + vt + uh
   

def draw(G, **kwargs):
    r"""
    This functions are only implemented for magnetic graphs. If
    you are trying to plot a NetworkX graph we encourage you to 
    use NetworkX methods.
    """
    from matplotlib.collections import LineCollection

    default_kwargs = {
        "layoyt": "spring_layout",
        "node_pos": None,
        "node_visible": True,
        "node_color": '#003050',
        "node_size": 40,
        "node_shape": 'o',
        "node_alpha": 1,
        "node_border_width": 1.0,
        "node_border_alpha": 1,
        "node_border_color": '#101010',
        "node_label": None,
        "edge_visible": True,
        "edge_width": 0.5,
        "edge_color": '#000000',
        "edge_alpha": 1,
        "edge_label": None,
        "edge_arrow_size": 10,
        "draw_potential": False,
        "hide_ticks": True, 
        "theta_sep": 0.075,
    }
    # check all kwargs are allowed
    for kwarg in kwargs:
        assert kwarg in default_kwargs, f"Invalid argument: {kwarg}"

    # Get currenx axes
    ax = plt.gca()
    # TODO: Plot only visible nodes --> creating a subgraph of visible nodes
    # Check if there are nodes already defined

    node_coordinates = None
    node_pos = kwargs.get("node_pos", default_kwargs["node_pos"])
    if isinstance(node_pos, dict):
        node_coordinates = {}
        node_coordinates.update(kwargs["node_pos"])

        for u, pos in node_coordinates.items():
            assert u in G.nodes, "node_pos keys must be nodes"
            assert len(pos) == 2, "Coordinates must be a 2 items array"

    # Check if it's linked to some node attribute
    elif node_pos != None:
        node_coordinates = {}
        for u in G.nodes:
            if node_pos in G.nodes[u]:
                node_coordinates[u] = G.nodes[u][node_pos]

        if len(node_coordinates) == 0:
            node_coordinates = None

    fixed = list(node_coordinates.keys()) if isinstance(node_coordinates, dict) else None
    node_coordinates = spring_layout(G, pos=node_coordinates, fixed=fixed)

    # Draw nodes
    positions = np.array(list(node_coordinates.values()))
    ax.scatter(
        positions[:,0],
        positions[:,1],
        s = kwargs.get("node_size", default_kwargs["node_size"]),
        c = kwargs.get("node_color", default_kwargs["node_color"]),
        marker = kwargs.get("node_shape", default_kwargs["node_shape"]),
        alpha = kwargs.get("node_alpha", default_kwargs["node_alpha"]),
        linewidths = kwargs.get("node_border_width", default_kwargs["node_border_width"]),
        edgecolors = kwargs.get("node_border_color", default_kwargs["node_border_color"]),
        zorder=2,
    )

    edges = G.edges(keys=True)
    edges_to_draw = {e: True for e in edges}

    edge_line_collection = []
    edge_colors_collection = []
    for e in edges:
        if edges_to_draw[e]:
            # Number of edges to plot between e[0] and e[1]
            keys01 = list(G._adj[e[0]][e[1]].keys())
            keys10 = []
            if not G.sym:
                keys10 = list(G._adj[e[1]].get(e[0],{}).keys())

            for key in keys01:
                edges_to_draw[(e[0],e[1],key)] = False
                if G.sym:
                    edges_to_draw[(e[1],e[0],key)] = False

            for key in keys10:
                edges_to_draw[(e[1],e[0],key)] = False

            k = len(keys01) + len(keys10)

            if  k == 1:
                thetas = [0]
            else:
                th = kwargs.get("theta_sep", default_kwargs["theta_sep"])
                thetas = np.linspace(-th * (k//2), 
                                     th * (k//2), 
                                     k)
                
            p0, p1 = node_coordinates[e[0]], node_coordinates[e[1]]
            for i in range(len(keys01)+len(keys10)):
                edge_line_collection.append(_arc(p0,p1,thetas[i]))
                edge_colors_collection.append(
                    kwargs.get("edge_color",
                                    default_kwargs["edge_color"]))
                
    line_collection = LineCollection(edge_line_collection,
                                     colors=edge_colors_collection,
                                     linewidths= kwargs.get("edge_width", 
                                                            default_kwargs["edge_width"]),
                                     zorder=1,
                                     alpha = kwargs.get("edge_alpha",
                                                        default_kwargs["edge_alpha"])
                                     )
    ax.add_collection(line_collection)  
    
    return ax


# TODO
def draw_frames(F, A, **kwargs):
    pass