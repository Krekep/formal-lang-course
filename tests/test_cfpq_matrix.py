import networkx as nx
import pytest
from pyformlang.cfg import CFG

from project.cfpq import cfpq_by_matrix


def _create_graph(nodes, edges) -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(
        list(map(lambda edge: (edge[0], edge[2], {"label": edge[1]}), edges))
    )
    return graph


@pytest.mark.parametrize(
    "actual,expected",
    [
        (
            cfpq_by_matrix(
                cfg=CFG.from_text(
                    """
                        S -> A B
                        A -> a
                        B -> b
                    """
                ),
                graph=_create_graph(nodes=[0, 1, 2], edges=[(0, "a", 1), (1, "b", 2)]),
            ),
            {(0, 2)},
        ),
        (
            cfpq_by_matrix(
                cfg=CFG.from_text(
                    """
                        S -> $
                    """
                ),
                graph=_create_graph(nodes=[0, 1], edges=[(0, "a", 1), (1, "b", 0)]),
            ),
            {(0, 0), (1, 1)},
        ),
        (
            cfpq_by_matrix(
                cfg=CFG.from_text(
                    """
                        S -> A B C
                        A -> a
                        B -> b
                        C -> c
                    """
                ),
                graph=_create_graph(
                    nodes=[0, 1, 2, 3], edges=[(0, "a", 1), (1, "b", 2), (2, "c", 3)]
                ),
            ),
            {(0, 3)},
        ),
        (
            cfpq_by_matrix(
                cfg=CFG.from_text(
                    """
                        S -> A B C | S S | s
                        A -> a
                        B -> b
                        C -> c
                    """
                ),
                graph=_create_graph(
                    nodes=[0, 1, 2, 3],
                    edges=[(0, "s", 0), (0, "a", 1), (1, "b", 2), (2, "c", 3)],
                ),
            ),
            {(0, 3), (0, 0)},
        ),
        (
            cfpq_by_matrix(
                cfg=CFG.from_text(
                    """
                        S -> A B S S C
                        A -> a | $
                        B -> b
                        C -> S
                        C -> $
                    """
                ),
                graph=_create_graph(
                    nodes=[0, 1, 2, 3, 4],
                    edges=[(0, "a", 1), (1, "b", 2), (2, "a", 3), (3, "b", 4)],
                ),
            ),
            set(),
        ),
    ],
)
def test_context_free_path_query(actual: set[tuple], expected: set[tuple]):
    assert actual == expected
