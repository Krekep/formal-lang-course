import cfpq_data
import pytest
from project import utils

_test_graph = cfpq_data.labeled_two_cycles_graph(
    10, 5, edge_labels=("a", "b"), verbose=False
)


def test_get_nodes():
    g_info = utils.get_graph_info(_test_graph)
    assert g_info[0] == 16


def test_get_edges():
    g_info = utils.get_graph_info(_test_graph)
    assert g_info[1] == 17


def test_get_labels():
    g_info = utils.get_graph_info(_test_graph)
    assert g_info[2] == {"a", "b"}
