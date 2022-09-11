import argparse
import project
from project import manager

__all__ = ["parser_initialize"]


def parser_initialize() -> argparse.ArgumentParser:
    """
    Parses console input when starting a module

    Returns
    -------
    argparse.ArgumentParser
        Commands parser
    """
    parser = argparse.ArgumentParser(prog="python -m project")
    parser.set_defaults(func=lambda args: parser.error("too few arguments"))
    subparsers = parser.add_subparsers(title="graph utilities", dest="")

    # print-graph-info
    parser_print_graph_info = subparsers.add_parser(
        "print-graph-info", help="Prints graph info. Specify graph name as a parameter."
    )
    parser_print_graph_info.add_argument(
        "graph_name", metavar="graph-name", help="name of desired graph"
    )
    parser_print_graph_info.set_defaults(func=manager.get_graph_info)

    # create-graph
    parser_gen_graph = subparsers.add_parser("create-graph", help="Create graph.")
    parser_gen_graph.set_defaults(
        func=lambda args: parser_gen_graph.error("too few arguments")
    )
    gen_graph_subparsers = parser_gen_graph.add_subparsers()

    # create-two-cycles
    parser_gen_graph_two_cycles = gen_graph_subparsers.add_parser(
        "two-cycles", help="Generates two cycles graph."
    )
    parser_gen_graph_two_cycles.add_argument(
        "graph_name", metavar="graph-name", help="graph name"
    )
    parser_gen_graph_two_cycles.add_argument(
        "first_cycle_nodes",
        metavar="first-cycle-nodes",
        help="number of nodes in the first cycle",
    )
    parser_gen_graph_two_cycles.add_argument(
        "second_cycle_nodes",
        metavar="second-cycle-nodes",
        help="number of nodes in the second cycle",
    )
    parser_gen_graph_two_cycles.add_argument(
        "--edge-labels",
        dest="edge_labels",
        help='edge labels for the first and second cycle (default "a", "b")',
        metavar=("L1", "L2"),
        default=["a", "b"],
        nargs=2,
    )
    parser_gen_graph_two_cycles.set_defaults(func=manager.create_two_cycles)

    # save-to-dot
    parser_save_to_dot = subparsers.add_parser(
        "save-to-dot", help="Save graph to dot file."
    )
    parser_save_to_dot.add_argument(
        "graph_name", metavar="graph-name", help="name of desired graph"
    )
    parser_save_to_dot.add_argument(
        "folder_path", metavar="folder-path", help="path to folder"
    )
    parser_save_to_dot.set_defaults(func=manager.save_to_dot)

    # quit
    parser_quit = subparsers.add_parser("quit", help="Stop executable.")
    parser_quit.set_defaults(func=manager.quit_comm)

    return parser
