"""
A set of methods for working with a graph.
"""

from typing import Tuple
from collections import namedtuple
from pathlib import Path
import cfpq_data
import networkx as nx


GraphInfo = namedtuple("GraphInfo", "nodes edges labels")


def get_graph_info(graph: nx.MultiDiGraph) -> GraphInfo:
    """
    Gets information about the graph as a tuple of 3 elements -
    the number of nodes, the number of edges, and labels set on the edges.

    Parameters
    ----------
    graph: nx.MultiDiGraph
        Graph from which information is gained

    Returns
    -------
    info: GraphInfo
        Namedtuple of (number of nodes, number of edges, set of edges' labels)
    """

    return GraphInfo(
        graph.number_of_nodes(),
        graph.number_of_edges(),
        set(attributes["label"] for (_, _, attributes) in graph.edges.data()),
    )


def create_two_cycle_graph(
    first_vertices: int, second_vertices: int, edge_labels: Tuple[str, str]
) -> nx.MultiDiGraph:
    """
    Create two cycle graph with labels on the edges.

    Parameters
    ----------
    first_vertices: int
        Amount of vertices in the first cycle
    second_vertices: int
        Amount of vertices in the second cycle
    edge_labels: Tuple[str, str]
        Labels for the edges on the first and second cycle

    Returns
    -------
    nx.MultiDiGraph
        Generated graph with two cycles
    """
    return cfpq_data.labeled_two_cycles_graph(
        first_vertices, second_vertices, labels=edge_labels
    )


def export_graph_to_dot(
    graph: nx.MultiDiGraph, graph_name: str, folder_path: str
) -> str:
    """
    Export given graph to .dot script

    Parameters
    ----------
    graph: nx.MultiDiGraph
        Graph for export
    graph_name: str
        Name of graph
    folder_path: str
        Path to export folder

    Returns
    -------
    result_path: str
        Path to result script
    """

    graph_dot = nx.drawing.nx_pydot.to_pydot(graph)
    result_path = f"{folder_path}/{graph_name}.dot"
    result_file = Path(result_path)

    if not result_file.is_file():
        open(result_file, "w")

    graph_dot.write_raw(result_path)

    return result_path
