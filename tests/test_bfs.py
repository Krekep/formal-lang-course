import cfpq_data
import pytest
import networkx as nx
from pyformlang.regular_expression import Regex

from project.rpq import bfs_rpq


def _create_graph(nodes: list[int], edges: list[tuple[int, str, int]]) -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(
        list(map(lambda edge: (edge[0], edge[2], {"label": edge[1]}), edges))
    )
    return graph


testdata_separated = [
    (
        bfs_rpq(
            _create_graph(nodes=[0, 1], edges=[(0, "a", 1)]), "a*", start_vertices={0}, final_vertices=None, separated=True,
        ),
        {(0, frozenset([1]))},
    ),
    (
        bfs_rpq(
            cfpq_data.labeled_two_cycles_graph(2, 1, labels=("a", "b")), "b.a",
            start_vertices={0}, final_vertices=None, separated=True,
        ),
        {(0, frozenset({1, 3}))},
    ),
    (
        bfs_rpq(
            _create_graph(nodes=[0, 1, 2], edges=[(0, "a", 1), (1, "a", 2)]), "a*",
            start_vertices={0, 1}, final_vertices={2}, separated=True,
        ),
        {(1, frozenset({2})), (0, frozenset({2}))},
    ),
    (
        bfs_rpq(
            _create_graph(nodes=[0, 1, 2], edges=[(0, "a", 1), (1, "b", 2)]), "a.b",
            start_vertices={0}, final_vertices=None, separated=False,
        ),
        {(frozenset({0}), frozenset({1, 2}))},
    ),
    (
        bfs_rpq(
            _create_graph(nodes=[0, 1, 2], edges=[(0, "a", 1), (1, "a", 2)]), "a*",
            start_vertices={0, 1}, final_vertices=None, separated=False,
        ),
        {(frozenset({0, 1}), frozenset({1, 2}))},
    )
]


@pytest.mark.parametrize("actual,expected", testdata_separated)
def test_bfs_based_regular_path_query(actual: set[any], expected: set[any]):
    assert actual == expected
