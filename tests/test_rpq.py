import pytest
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State, DeterministicFiniteAutomaton

from project.utils import automaton_to_matrix, intersect, matrix_to_automaton, get_transitive_closure, rpq, \
    create_two_cycle_graph


def test_transitive_closure():
    nfa = NondeterministicFiniteAutomaton()
    nfa.add_transitions(
        [
            (0, "a", 1),
            (0, "a", 2),
            (2, "d", 3),
            (1, "c", 1),
            (1, "b", 2),
            (3, "d", 0),
        ]
    )
    matrix, size, start, final, states = automaton_to_matrix(nfa)
    tc = get_transitive_closure(matrix)
    assert tc.sum() == tc.size


def test_intersection():
    first_nfa = NondeterministicFiniteAutomaton()
    first_nfa.add_transitions(
        [(0, "a", 1), (0, "c", 1), (0, "c", 0), (1, "b", 1), (1, "c", 2), (2, "d", 0)]
    )
    first_nfa.add_start_state(State(0))
    first_nfa.add_final_state(State(0))
    first_nfa.add_final_state(State(1))
    first_nfa.add_final_state(State(2))

    second_nfa = NondeterministicFiniteAutomaton()
    second_nfa.add_transitions([(0, "a", 1), (0, "a", 0), (1, "b", 1), (1, "e", 2)])
    second_nfa.add_start_state(State(0))
    second_nfa.add_final_state(State(1))

    expected_nfa = first_nfa.get_intersection(second_nfa)

    intersected_matrix, intersected_size, intersected_start, intersected_final, intersected_states = intersect(
        first_nfa, second_nfa)

    actual_nfa = matrix_to_automaton(intersected_matrix, intersected_start, intersected_final)

    assert actual_nfa.is_equivalent_to(expected_nfa)


@pytest.mark.parametrize(
    "regex,start_nodes,final_nodes,expected_rpq",
    [
        ("x* | y", {0}, {1, 2, 3, 4}, {(0, 1), (0, 2), (0, 3), (0, 4)}),
        ("x* | y", {4}, {4, 5}, {(4, 5)}),
        ("x x", {0, 1, 2, 3}, {0, 1, 2, 3}, {(0, 2), (1, 3), (2, 0), (3, 1)}),
        ("y", {0}, {0, 1, 2, 3}, set()),
        ("y*", {0}, {5, 4}, {(0, 5), (0, 4)}),
    ],
)
def test_querying(regex, start_nodes, final_nodes, expected_rpq):
    graph = create_two_cycle_graph(3, 2, ("x", "y"))
    actual_rpq = rpq(graph, regex, start_nodes, final_nodes)

    assert actual_rpq == expected_rpq
