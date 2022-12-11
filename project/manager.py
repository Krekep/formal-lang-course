import sys
from argparse import Namespace

import cfpq_data
import networkx as nx

from project import graph_utils

__all__ = [
    "get_graph_info",
    "create_two_cycles",
    "save_to_dot",
    "quit_comm",
]

_graph_pool = {}


def get_graph_info(args: Namespace) -> None:
    """
    This method provide use get_graph_info with console arguments.
    Return information about graph by its name.

    Parameters
    ----------
    args: argparse.Namespace
        Parsed arguments

    Returns
    -------
    None
    """

    info = graph_utils.get_graph_info(get_graph(args.graph_name))

    print("Graph information:")
    print("Number of nodes: ", info.nodes)
    print("Number of edges: ", info.edges)
    print("Labels: ", *(info.labels))


def create_two_cycles(args: Namespace) -> None:
    """
    This method provide use create_two_cycles and export_graph_to_dot with console arguments.
    Create named and labeled graph with two cycles and export to .dot file.

    Parameters
    ----------
    args: argparse.Namespace
        Parsed arguments

    Returns
    -------
    None
    """

    graph = graph_utils.create_two_cycle_graph(
        int(args.first_cycle_nodes), int(args.second_cycle_nodes), args.edge_labels
    )

    _graph_pool[args.graph_name] = graph

    path_to_dot_script = graph_utils.export_graph_to_dot(
        graph, args.graph_name, args.folder_path
    )

    print(f"Graph '{args.graph_name}' have been created.")
    print(f"Graph was saved in {path_to_dot_script}")


def save_to_dot(args: Namespace) -> None:
    """
    This method provide use save_to_dot with console arguments.
    Saves given graph to the dot file by folder_path.

    Parameters
    ----------
    args: argparse.Namespace
        Parsed arguments

    Returns
    -------
    None
    """

    graph = get_graph(args.graph_name)

    path_to_dot_script = graph_utils.export_graph_to_dot(
        graph, args.graph_name, args.folder_path
    )

    print(f"Graph was saved in {path_to_dot_script}")


def get_graph(graph_name: str) -> nx.MultiDiGraph:
    """
    Return graph by name

    Parameters
    ----------
    graph_name: str
        Graph name

    Returns
    -------
    nx.MultiDiGraph
        Resulting graph
    """

    graph = None
    graphs_in_cfpq = cfpq_data.DATASET
    if graph_name in graphs_in_cfpq:
        graph_path = cfpq_data.download(graph_name)
        graph = cfpq_data.graph_from_csv(graph_path)

    if graph_name in _graph_pool.keys():
        graph = _graph_pool[graph_name]

    if graph is None:
        raise Exception(f"No {graph_name} graph exists!")

    return graph


def quit_comm(args: Namespace) -> None:
    """
    This method terminates the entire application using sys.exit(0).

    Parameters
    ----------
    args: argparse.Namespace
        Parsed arguments

    Returns
    -------
    None
    """
    print("Quit...")
    sys.exit(0)
