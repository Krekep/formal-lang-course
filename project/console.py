from typing import List

from . import bridge

__all__ = ["run_console"]


_command_names = ["get_graph_info", "create_two_cycles", "save_to_dot", "quit"]
_function_pointers = {
    _command_names[0]: (1, bridge.get_graph_info),
    _command_names[1]: (5, bridge.create_two_cycles),
    _command_names[2]: (2, bridge.save_to_dot),
    _command_names[3]: (0, bridge.quit_comm),
}


def _exec_commands(commands: List[str]) -> None:
    """
    This method tries to execute user input.
    Parameters
    ----------
    commands: List[str]
        List of arguments to execute
    Returns
    -------
    None
    """
    is_command = False

    for comm_name in _command_names:
        if (
            commands[0] == comm_name
            and _function_pointers[comm_name][0] == len(commands) - 1
        ):
            is_command = True
            try:
                _function_pointers[comm_name][1](*commands[1:])
            except Exception as e:
                print(e)

    if not is_command:
        print("Invalid command")


def _help() -> None:
    """
    Display information about available commands.
    Returns
    -------
    None
    """
    print(
        "\n(1) get_graph_info [graph_name] : Get info about graph - number of nodes, number of edges, labels;"
    )
    print(
        "(2) create_two_cycles [graph_name] [nodes_number_first] [nodes_number_second] [label_1] [label_2]: Create "
        "graph with two cycles;"
    )
    print(
        "(3) save_to_dot [graph_name] [folder_path]: Save graph with graph_name to dot file in folder_path;"
    )
    print("(4) quit : Stop executable.")


def run_console() -> None:
    """
    Runs a console application.
    Returns
    -------
    None
    """
    _help()

    while True:
        stream = input(">>> ")
        commands = stream.split()

        _exec_commands(commands)
