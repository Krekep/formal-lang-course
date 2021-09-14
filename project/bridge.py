import sys
from pathlib import Path
from typing import Tuple

import cfpq_data
import networkx as nx
import project.utils
from project import utils

__all__ = ["get_graph_info", "create_two_cycles", "save_to_dot", "quit_comm"]

_graph_pool = {}


def get_graph_info(graph_name: str) -> Tuple[int, int, set]:
    """
    This method provide use get_graph_info with console arguments.
    Return information about graph by its name.

    Parameters
    ----------
    graph_name: str
        Name of the graph

    Returns
    -------
    Tuple[int, int, set]
        Amount of nodes and edges and a set of labels for the graph with following name
    """

    is_graph_exist = False
    info = (None, None, None)

    for graph_class in cfpq_data.DATASET.keys():
        if graph_name in cfpq_data.DATASET[graph_class].keys():
            is_graph_exist = True
            graph = cfpq_data.graph_from_dataset(graph_name, verbose=False)
            info = utils.get_graph_info(graph)
            break

    if graph_name in _graph_pool.keys():
        info = utils.get_graph_info(_graph_pool[graph_name])
        is_graph_exist = True

    if not is_graph_exist:
        raise Exception("No such graph exists!")

    print("Graph information:")
    print("Number of nodes: ", info[0])
    print("Number of edges: ", info[1])
    print("Labels: ", *(info[2]))
    return info[0], info[1], info[2]


def create_two_cycles(
    graph_name: str,
    first_vertices: str,
    second_vertices: str,
    first_label: str,
    second_label: str,
) -> None:
    """
    This method provide use create_two_cycles with console arguments.
    Create named and labeled graph with two cycles.

    Parameters
    ----------
    graph_name: str
        Name of the created graph
    first_vertices: str
        Amount of vertices in the first cycle as string
    second_vertices: str
        Amount of vertices in the second cycle as string
    first_label: str
        Label for edges in the first cycle
    second_label: str
        Label for edges in the second cycle

    Returns
    -------
    None
    """

    graph = utils.create_two_cycle_graph(
        int(first_vertices), int(second_vertices), (first_label, second_label)
    )

    _graph_pool[graph_name] = graph

    print(f"Graph '{graph_name}' have been created.")


def save_to_dot(graph_name: str, folder_path: str) -> str:
    """
    This method provide use save_to_dot with console arguments.
    Saves given graph to the dot file by folder_path.

    Parameters
    ----------
    graph_name: str
        Name of saved graph
    folder_path: str
        Path to the folder where to save graph

    Returns
    -------
    str
        Related path to the .dot file with graph
    """

    if graph_name not in _graph_pool.keys():
        raise Exception("No graph exist with this name!")

    graph = _graph_pool[graph_name]

    graph_dot = nx.drawing.nx_pydot.to_pydot(graph)
    result_path = f"{folder_path}/{graph_name}.dot"
    result_file = Path(result_path)

    if not result_file.is_file():
        open(result_file, "w")

    graph_dot.write_raw(result_path)

    print(f"Graph was saved in {result_path}")
    return result_path


def quit_comm() -> None:
    """
    This method terminates the entire application using sys.exit(0).

    Returns
    -------
    None
    """
    print("Quit...")
    sys.exit(0)
