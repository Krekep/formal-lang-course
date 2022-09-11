import cfpq_data
import pytest
from project import graph_utils

_test_graph = cfpq_data.labeled_two_cycles_graph(10, 5, labels=("a", "b"))


def test_get_nodes():
    g_info = graph_utils.get_graph_info(_test_graph)
    assert g_info.nodes == 16


def test_get_edges():
    g_info = graph_utils.get_graph_info(_test_graph)
    assert g_info.edges == 17


def test_get_labels():
    g_info = graph_utils.get_graph_info(_test_graph)
    assert g_info.labels == {"a", "b"}
