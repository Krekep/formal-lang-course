import sys
from argparse import Namespace
from pathlib import Path
from typing import Tuple

import cfpq_data
import networkx as nx
import pyformlang
from pyformlang.finite_automaton import EpsilonNFA

import project.utils
from project import utils

__all__ = [
    "get_graph_info",
    "create_two_cycles",
    "save_to_dot",
    "quit_comm",
    "graph_to_nfa",
    "get_graph",
]

_graph_pool = {}
_nfa_pool = {}


def graph_to_nfa(args: Namespace) -> None:
    """
    This method provide use graph_to_nfa with console arguments.
    Construction of a non-deterministic automaton from a labeled graph.

    Parameters
    ----------
    args: argparse.Namespace
        Parsed arguments

    Returns
    -------
    None
    """

    graph = get_graph(args.graph_name)

    nfa = utils.graph_to_nfa(graph)
    _nfa_pool[args.graph_name] = nfa

    print("Successful translated")


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

    info = get_graph(args.graph_name)

    print("Graph information:")
    print("Number of nodes: ", info[0])
    print("Number of edges: ", info[1])
    print("Labels: ", *(info[2]))


def create_two_cycles(args: Namespace) -> None:
    """
    This method provide use create_two_cycles with console arguments.
    Create named and labeled graph with two cycles.

    Parameters
    ----------
    args: argparse.Namespace
        Parsed arguments

    Returns
    -------
    None
    """

    graph = utils.create_two_cycle_graph(
        int(args.first_cycle_nodes), int(args.second_cycle_nodes), args.edge_labels
    )

    _graph_pool[args.graph_name] = graph

    print(f"Graph '{args.graph_name}' have been created.")


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

    if args.graph_name not in _graph_pool.keys():
        raise Exception("No graph exist with this name!")

    graph = _graph_pool[args.graph_name]

    graph_dot = nx.drawing.nx_pydot.to_pydot(graph)
    result_path = f"{args.folder_path}/{args.graph_name}.dot"
    result_file = Path(result_path)

    if not result_file.is_file():
        open(result_file, "w")

    graph_dot.write_raw(result_path)

    print(f"Graph was saved in {result_path}")


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

    is_graph_exist = False
    graph = None

    for graph_class in cfpq_data.DATASET.keys():
        if graph_name in cfpq_data.DATASET[graph_class].keys():
            is_graph_exist = True
            graph = cfpq_data.graph_from_dataset(graph_name, verbose=False)
            break

    if graph_name in _graph_pool.keys():
        graph = _graph_pool[graph_name]
        is_graph_exist = True

    if not is_graph_exist:
        raise Exception("No such graph exists!")

    return graph
