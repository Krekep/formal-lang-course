import cfpq_data
import pytest
from project import graph_utils

_expected_graph = cfpq_data.labeled_two_cycles_graph(10, 5, labels=("a", "b"))
_actual_graph = graph_utils.create_two_cycle_graph(10, 5, edge_labels=("a", "b"))


def test_num_nodes():
    assert _actual_graph.number_of_nodes() == _expected_graph.number_of_nodes()


def test_num_edges():
    assert _actual_graph.number_of_edges() == _expected_graph.number_of_edges()


def test_labels():
    actual_labels = set(attributes["label"] for (_, _, attributes) in _actual_graph.edges.data())
    expected_labels = set(attributes["label"] for (_, _, attributes) in _actual_graph.edges.data())
    assert actual_labels.__eq__(expected_labels)
