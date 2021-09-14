import networkx
import pydot

from project import bridge, utils


_saved_graph_name = "test_saving"
_expected_graph = "expected_saving"


def _save_default_graph() -> str:
    """
    This method creates and saves a predefined graph.
    Returns
    -------
    str
        Path to saved graph
    """
    bridge.create_two_cycles(_saved_graph_name, "10", "5", "a", "b")
    path = bridge.save_to_dot(_saved_graph_name, "tests/data")
    return path


def test_saving_equivalence():
    path = _save_default_graph()
    saved_file = open(path, "r")
    expected_file = open(f"tests/data/{_expected_graph}.dot", "r")
    assert saved_file.read() == expected_file.read()


def test_saving_to_dot_path():
    path = _save_default_graph()
    assert path == f"tests/data/{_saved_graph_name}.dot"


def test_saving_to_dot_nodes():
    _save_default_graph()
    pydot_graph = pydot.graph_from_dot_file(f"tests/data/{_saved_graph_name}.dot")[0]
    graph = networkx.drawing.nx_pydot.from_pydot(pydot_graph)
    info = utils.get_graph_info(graph)
    assert info[0] == 16


def test_saving_to_dot_edges():
    _save_default_graph()
    pydot_graph = pydot.graph_from_dot_file(f"tests/data/{_saved_graph_name}.dot")[0]
    graph = networkx.drawing.nx_pydot.from_pydot(pydot_graph)
    info = utils.get_graph_info(graph)
    assert info[1] == 17


def test_saving_to_dot_labels():
    _save_default_graph()
    pydot_graph = pydot.graph_from_dot_file(f"tests/data/{_saved_graph_name}.dot")[0]
    graph = networkx.drawing.nx_pydot.from_pydot(pydot_graph)
    info = utils.get_graph_info(graph)
    assert info[2] == {"a", "b"}
