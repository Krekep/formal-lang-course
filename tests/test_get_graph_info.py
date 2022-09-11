import cfpq_data
import pytest
from project import graph_utils

_test_graph = graph_utils.create_two_cycle_graph(
    10, 5, edge_labels=("a", "b")
)


def test_get_nodes():
    g_info = graph_utils.get_graph_info(_test_graph)
    assert g_info[0] == 16


def test_get_edges():
    g_info = graph_utils.get_graph_info(_test_graph)
    assert g_info[1] == 17


def test_get_labels():
    g_info = graph_utils.get_graph_info(_test_graph)
    assert g_info[2] == {"a", "b"}
