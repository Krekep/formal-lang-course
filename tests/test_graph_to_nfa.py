import cfpq_data
import pytest

import project
from project import graph_utils

from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State


_test_graph = cfpq_data.labeled_two_cycles_graph(2, 2, labels=("a", "b"))


def test_is_not_deterministic():
    nfa = graph_utils.graph_to_nfa(_test_graph)
    assert not nfa.is_deterministic()


@pytest.mark.parametrize(
    "start_vertices, finish_vertices",
    [
        (None, None),
        ([0], [1]),
        ([0, 1], [3, 4]),
        ([0, 1, 2], [2, 3, 4]),
        ([0, 1, 2, 3], [1, 2, 3, 4]),
        ([0, 1, 2, 3, 4], [0, 1, 2, 3, 4]),
    ],
)
def test_nfa_equals(start_vertices, finish_vertices):
    expected_nfa = NondeterministicFiniteAutomaton()
    expected_nfa.add_transitions(
        [(1, "a", 2), (2, "a", 0), (0, "a", 1), (0, "b", 3), (3, "b", 4), (4, "b", 0)]
    )

    if start_vertices is None:
        start_vertices = [0, 1, 2, 3, 4]
    if finish_vertices is None:
        finish_vertices = [0, 1, 2, 3, 4]

    for state in start_vertices:
        expected_nfa.add_start_state(State(state))
    for state in finish_vertices:
        expected_nfa.add_final_state(State(state))

    nfa_from_graph = graph_utils.graph_to_nfa(_test_graph, start_vertices, finish_vertices)

    assert nfa_from_graph.is_equivalent_to(expected_nfa)


@pytest.mark.parametrize(
    "word, is_accept",
    [
        ("", False),
        ("a", True),
        ("aa", False),
        ("aaa", False),
        ("aaaa", True),
        ("ab", False),
        ("aaab", True),
        ("ba", True),
        ("bbba", True),
        ("b", True),
        ("bb", True),
        ("bbb", False),
        ("bbbb", True),
    ],
)
def test_word_accept(word, is_accept):
    nfa = graph_utils.graph_to_nfa(_test_graph, [0, 4], [1, 3])
    assert nfa.accepts(word) == is_accept

