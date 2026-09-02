from specnet.magraph import MagGraph
from specnet.frames.frame_graphs import FrameFamily

import matplotlib.pyplot as plt
import numpy as np

def _supported_color(c):
    r"""
    This function returns a bool encoding if the 
    color 'c' is  supported in matplotlib.colors (mcolors). 
    The possible colors are:
        - str with color name. A name of a color  in one of
        the lists mcolors.BASE_COLORS, mcolors.TABLEAU_COLORS,
        mcolors.CSS4_COLORS

        - str with HEX code. (#------)

        - rgb or rgba tuple. (0-1, 0-1, 0-1) or (0-1, 0-1, 0-1, 0-1)

    Parameters
    ----------
        c : any value
    
    Returns
    -------
        Bool encoding if `c` is a supported color in matplotlib.
    """
    import matplotlib.colors as mcolors

    colors_name = list(mcolors.BASE_COLORS.keys())
    colors_name += list(mcolors.TABLEAU_COLORS.keys())
    colors_name += list(mcolors.CSS4_COLORS.keys())

    if isinstance(c, str):
        # c must be HEX color or color name
        if c[0] == '#' and len(c) == 7:
            return True

        elif c in colors_name:
            return True

    elif isinstance(c, tuple):
        if len(c) == 3 or len(c) == 4:
            return True

    return  False


def _node_layout(G, node_pos=None):

    from networkx.drawing.layout import spring_layout

    node_coordinates = None
    if isinstance(node_pos, dict):
        node_coordinates = {}
        node_coordinates.update(node_pos)

        for u, pos in node_coordinates.items():
            assert u in G.nodes, "node_pos keys must be nodes"
            assert len(pos) == 2, "Coordinates must be a (2,)-array"

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

    return node_coordinates


def _arc(p0, p1, theta, k = 100):
    r"""
    This functions returns a (k, 2)-array
    with the points defining an arc that gpes 
    from p0 to p1 with incidence angle theta.

    Parameters
    ----------
        - p0 : ((2,)-array) tail point
        - p1 : ((2,)-array) head point
        - theta : (float) incidence angle
        - k : optional int (default = 100)
            linspace partition
    
    Returns
    -------
        - (k, 2)-array with the points defining
        the arc between p0 and p1

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


def _rotation(v, theta):
    dx = v[0] * np.cos(theta) - v[1] * np.sin(theta)
    dy = v[0] * np.sin(theta) + v[1] * np.cos(theta)
    return np.array([dx, dy])

def _angle(v1, v2):
    n1 = np.sqrt(v1[0] + v1[1])
    n2 = np.sqrt(v2[0] + v2[1])
    if v2@_rotation(v1, np.pi/2) < 0:
        return 2 * np.pi - np.acos((v1 @ v2)/(n1 * n2))
    else:
        return np.acos((v1 @ v2)/(n1 * n2))


def _loop(p0, r, phi_0, theta, k=100):
    pass


def draw(G, **kwargs):
    r"""
    This functions are only implemented for magnetic graphs. If
    you are trying to plot a NetworkX graph we encourage you to 
    use NetworkX methods.
    """
    from matplotlib.collections import LineCollection
    from collections import defaultdict

    import networkx as nx

    default_kwargs = {
        "layoyt": "spring_layout",
        "node_pos": None,
        "node_visible": True,
        "node_color": '#003050',
        "node_size": 40,
        "node_shape": 'o',
        "node_alpha": 1,
        "node_border_width": 1.0,
        "node_border_color": '#101010',
        "node_label": None,
        "edge_visible": True,
        "edge_width": 0.5,
        "edge_color": '#000000',
        "edge_alpha": 1,
        "edge_label": None,
        "edge_arrow_size": 10,
        "draw_potential": False,
        "theta_sep": 0.075,
        "hide_ticks": True, 
        "hide_axis": False,
    }

    # check all kwargs are allowed
    for kwarg in kwargs:
        assert kwarg in default_kwargs, f"Invalid argument: {kwarg}"

    # Get currenx axes
    ax = plt.gca()

    # ====================  Draw nodes  ====================================
    # TODO Get only visible nodes
    # Get node attributes
    # pos
    node_coordinates = _node_layout(G, node_pos=kwargs.get("node_pos", None))
    positions = np.array(list(node_coordinates.values()))
    # color
    if _supported_color(kwargs.get("node_color", default_kwargs["node_color"])):
        colors = kwargs.get("node_color", default_kwargs["node_color"])
    
    else: # must be a key of the nodes
        if isinstance(kwargs["node_color"], dict):
            colors = nx.get_node_attributes(G, '', default_kwargs["node_color"])    
            colors.update(kwargs["node_color"])
        else:
            colors = nx.get_node_attributes(G, kwargs["node_color"], default_kwargs["node_color"])

        colors = list(colors.values())
    # linewidths
    node_border_width = kwargs.get('node_border_width', default_kwargs['node_border_width'])
    if isinstance(node_border_width, dict):
        node_border_width = nx.get_node_attributes(G, '', default_kwargs['node_border_width'])
        node_border_width.update(kwargs['node_border_width'])
        node_border_width = list(node_border_width.values())
    elif isinstance(node_border_width, str):
        node_border_width = nx.get_node_attributes(G, kwargs["node_border_width"], default_kwargs['node_border_width'])
        node_border_width = list(node_border_width.values())
    # edge_colors
    node_border_color = kwargs.get('node_border_color', default_kwargs['node_border_color'])
    if isinstance(node_border_color, dict):
        node_border_color = nx.get_node_attributes(G, '', default_kwargs['node_border_color'])
        node_border_color.update(kwargs['node_border_color'])
        node_border_color = list(node_border_color.values())
    elif not _supported_color(node_border_color):
        node_border_color = nx.get_node_attributes(G, kwargs["node_border_color"], default_kwargs['node_border_color'])
        node_border_color = list(node_border_color.values())
    # node_alpha
    node_alpha = kwargs.get('node_alpha', default_kwargs['node_alpha'])
    if isinstance(node_alpha, dict):
        node_alpha = nx.get_node_attributes(G, '', default_kwargs['node_alpha'])
        node_alpha.update(kwargs['node_alpha'])
        node_alpha = list(node_alpha.values())
    elif isinstance(node_alpha, str):
        node_alpha = nx.get_node_attributes(G, kwargs["node_alpha"], default_kwargs['node_alpha'])
        node_alpha = list(node_alpha.values())
    
    ax.scatter(
        positions[:,0],
        positions[:,1],
        s = kwargs.get("node_size", default_kwargs["node_size"]),
        c = colors,
        marker = kwargs.get("node_shape", default_kwargs["node_shape"]),
        alpha = node_alpha,
        linewidths = node_border_width,
        edgecolors = node_border_color,
        zorder=2,
    )

    # ====================  Draw edges  ====================================
    edges = G.edges(keys=True)
    edges_to_draw = {e: True for e in edges}

    edge_line_collection = []
    edge_colors_collection = []

    loops_collection = defaultdict(list)
    for e in edges:
        if edges_to_draw[e] and e[0]!=e[1]:
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

        elif e[0] == e[1]:
            loops_collection[e[0]].append(e[2])
            edges_to_draw[(e[0],e[1],e[2])] = False

    color_loops = []
    loops_line_collection = []
    for u, keys in loops_collection.items():
        thetas = {}
        for v in G._adj[u]:
            pos_u, pos_v = node_coordinates[u], node_coordinates[v]
            vec_uv = np.array([
                pos_v[0] - pos_u[0],
                pos_v[1] - pos_u[1],
            ])
            thetas[v] = _angle(np.array([1,0]), vec_uv)

        thetas = np.sort(thetas)
        thetas_in_space = list(np.diff(thetas)) + [2 * np.pi - thetas[-1] + thetas[0]]

        i_max = np.argmax(thetas_in_space)

    
                
    line_collection = LineCollection(edge_line_collection,
                                     colors=edge_colors_collection,
                                     linewidths= kwargs.get("edge_width", 
                                                            default_kwargs["edge_width"]),
                                     zorder=1,
                                     alpha = kwargs.get("edge_alpha",
                                                        default_kwargs["edge_alpha"]),
                                     )
    ax.add_collection(line_collection)  

    if kwargs.get("hide_axis", default_kwargs["hide_axis"]):
        ax.set_axis_off()
    elif kwargs.get("hide_ticks", default_kwargs["hide_ticks"]):
        ax.set_xticks([])
        ax.set_yticks([])

    return ax


def draw_frames(F, A, S1=[], **kwargs):
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
            "theta_sep": 0.075,
            "hide_ticks": True, 
            "hide_axis": False,
        }

    if isinstance(A, list):
        G = F.generate_r_frame(A, S1)
    elif isinstance(A, int):
        G = F.generate_frame(A)
    else:
        raise ValueError(
            f"Must introduce a list with int values or an int."+
                f"{A} is no soported"
        )

    node_coordinates = _node_layout(F.graph, node_pos=kwargs.get("node_pos", default_kwargs["node_pos"]))