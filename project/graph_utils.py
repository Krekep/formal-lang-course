"""
A set of methods for working with a graph.
"""

from typing import Tuple
import cfpq_data
import networkx as nx


def get_graph_info(graph: nx.MultiDiGraph) -> Tuple[int, int, set]:
    """
    Gets information about the graph as a tuple of 3 elements -
    the number of nodes, the number of edges, and labels set on the edges.

    Parameters
    ----------
    graph: nx.MultiDiGraph
        Graph from which information is gained

    Returns
    -------
    Tuple[int, int, set]
        Info about graph
    """
    return (
        graph.number_of_nodes(),
        graph.number_of_edges(),
        cfpq_data.get_labels(graph, verbose=False)
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
        first_vertices, second_vertices, edge_labels=edge_labels, verbose=False
    )
