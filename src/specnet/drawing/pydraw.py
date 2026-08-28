from specnet.magraph import MagGraph
from specnet.frames.frame_graphs import FrameFamily
from networkx.drawing.layout import spring_layout

import matplotlib.pyplot as plt

def draw(G, **kwargs):
    r"""
    This functions are only implemented for magnetic graphs. If
    you are trying to plot a NetworkX graph we encourage you to 
    use NetworkX methods.
    """
    default_kwargs = {
        "layoyt": "spring_layout",
        "node_pos": None,
        "node_visible": True,
        "node_color": '#000000',
        "node_size": 300,
        "node_shape": 'o',
        "node_alpha": 0.75,
        "node_border_width": 1.0,
        "node_border_alpha": 1,
        "node_border_color": '#000000',
        "node_label": None,
        "edge_visible": True,
        "edge_width": 1,
        "edge_color": '#704A6D',
        "edge_label": None,
        "draw_potential": False,
        "hide_ticks": True, 
    }
    # check all kwargs are allowed
    for kwarg in kwargs:
        assert kwarg in default_kwargs, f"Invalid argument: {kwarg}"


    # Check if there are nodes already defined
    node_coordinates = None
    if isinstance(kwargs["node_pos"], dict):
        node_coordinates.update(kwargs["node_pos"])

        for u, pos in node_coordinates.items():
            assert u in G.nodes, "node_pos keys must be nodes"
            assert len(pos) == 2, "Coordinates must be a 2 items array"

    # Check if it's linked to some node attribute
    elif kwargs["node_pos"] != None:
        node_pos = kwargs["node_pos"]
        node_coordinates = {}
        for u in G.nodes:
            if node_pos in G.nodes[u]:
                node_coordinates[u] = G.nodes[u][node_pos]
        if len(node_coordinates) == 0:
            node_coordinates = None

    fixed = list(node_coordinates.keys()) if isinstance(node_coordinates, dict) else None
    node_coordinates = spring_layout(G, pos=node_coordinates, fixed=fixed)

    return node_coordinates


# TODO
def draw_frames(F, A, **kwargs):
    pass