import networkx as nx
from IPython.display import Math
from IPython.display import display
from networkx.drawing.nx_pydot import graphviz_layout
from networkx.readwrite import json_graph


def plot_graph(expr):
    """
    Make a graph plot of the internal representation of SymPy expression.
    """

    all_nodes, node_list, link_list = make_graph(expr)

    # Create the graph from the lists of nodes and links:
    graph_json = {"nodes": node_list, "links": link_list}
    node_labels = {node['id']: node['name'] for node in graph_json['nodes']}
    for n in graph_json['nodes']:
        del n['name']
    graph = json_graph.node_link_graph(graph_json, directed=True, multigraph=False)

    # Layout and plot the graph
    pos = graphviz_layout(graph, prog="dot")

    nx.draw(graph.to_directed(), pos, labels=node_labels, node_shape="s", node_color="none",
            bbox=dict(facecolor="skyblue", edgecolor='black', boxstyle='round,pad=0.2'))


def make_graph(expr):

    node_list = []
    link_list = []
    all_nodes = []

    class Id:
        """A helper class for autoincrementing node numbers."""
        counter = 0

        @classmethod
        def get(cls):
            cls.counter += 1
            return cls.counter

    class Node:
        """Represents a single operation or atomic argument."""

        def __init__(self, label, expr_id, path, latex_expr):
            self.id = expr_id
            self.name = label
            self.path = path
            self.latex = latex_expr

        def __repr__(self):
            return self.name

    def name_for_expr(expr):
        name = ""
        if expr.is_Atom:
            name += str(expr)
        else:
            name += type(expr).__name__
        return name

    def _walk(parent, expr, arg_idx):
        """Walk over the expression tree recursively creating nodes and links."""
        node_path = parent.path + "/[{}]".format(arg_idx)
        node = Node(name_for_expr(expr), Id.get(), node_path, latex(expr))
        all_nodes.append(node)
        node_list.append({"id": node.id, "name": node.name})
        link_list.append({"source": parent.id, "target": node.id})

        if not expr.is_Atom:
            node_list.append({"id": node.id, "name": node.name})
            link_list.append({"source": parent.id, "target": node.id})
            for idx, arg in enumerate(expr.args):
                _walk(node, arg, idx)

    _walk(Node("Root", 0, "", ""), expr, 0)

    return all_nodes, node_list, link_list


def show_paths(expr):
    all_nodes, _, _ = make_graph(expr)
    for node in all_nodes:
        display(node.path, Math(node.latex))


if __name__ == '__main__':
    from sympy import *

    x, y, z, a, b, c = symbols("x, y, z, a, b, c")
    expr = c ** 2 + ((x + 1) ** 2 + (x - 1) ** 2) / (sqrt((x - 1) ** 2 + (x + 3) ** 2))

    show_paths(expr)
