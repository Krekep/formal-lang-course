import networkx as nx

import project
from project import parser
from project.utils import graph_to_nfa
from project.bridge import create_two_cycles, get_graph
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State, Symbol

import pytest

_graph_name = "test"


def create_default_graph():
    p = parser.parser_initialize()
    args = p.parse_args(f"create-graph two-cycles {_graph_name} 2 2".split())
    create_two_cycles(args)


@pytest.fixture
def default_nfa():
    nfa = NondeterministicFiniteAutomaton()
    nfa.add_transitions(
        [(1, "a", 2), (2, "a", 0), (0, "a", 1), (0, "b", 3), (3, "b", 4), (4, "b", 0)]
    )

    return nfa


@pytest.fixture
def default_start_states():
    return {1, 3}


@pytest.fixture
def default_final_states():
    return {2, 3}


@pytest.mark.parametrize(
    "start,final",
    [
        (None, None),
        ([1], [2]),
        ([0, 2, 3], [0, 2, 3]),
    ],
)
def test_nfa_is_equivalent(default_nfa, start: list, final: list):
    create_default_graph()
    if not start:
        start = [0, 1, 2, 3, 4]
    if not final:
        final = [0, 1, 2, 3, 4]

    nfa = default_nfa
    for state in start:
        nfa.add_start_state(State(state))
    for state in final:
        nfa.add_final_state(State(state))

    nfa_from_graph = graph_to_nfa(get_graph(_graph_name), start, final)

    assert nfa_from_graph.is_equivalent_to(nfa)


def test_not_deterministic():
    create_default_graph()
    nfa = graph_to_nfa(get_graph(_graph_name))
    return not nfa.is_deterministic()


@pytest.mark.parametrize(
    "word,expected_accept",
    [
        ("a", True),
        ("aab", True),
        ("", True),
        ("b", False),
        ("aa", False),
        ("ab", False),
    ],
)
def test_accepts_word(
    default_start_states, default_final_states, word, expected_accept
):
    create_default_graph()
    nfa = graph_to_nfa(
        get_graph(_graph_name), default_start_states, default_final_states
    )

    assert nfa.accepts(word) == expected_accept


def test_mismatch_states():
    create_default_graph()
    with pytest.raises(Exception):
        graph_to_nfa(get_graph(_graph_name), [0, 1, 2, 33], [0, 1, 2, 3])


def test_null_graph():
    graph = nx.null_graph(create_using=nx.MultiDiGraph)
    nfa_from_graph = graph_to_nfa(graph)

    assert nfa_from_graph.is_empty()


def test_empty_graph():
    graph = nx.empty_graph(2, create_using=nx.MultiDiGraph)
    nfa_from_graph = graph_to_nfa(graph)

    expected_nfa = NondeterministicFiniteAutomaton()
    expected_nfa.add_start_state(State(0))
    expected_nfa.add_start_state(State(1))
    expected_nfa.add_final_state(State(0))
    expected_nfa.add_final_state(State(1))

    assert nfa_from_graph.is_equivalent_to(expected_nfa)


def test_one_node_loop_graph():
    graph = nx.empty_graph(1, create_using=nx.MultiDiGraph)
    graph.add_edge(0, 0, label="0")
    nfa_from_graph = graph_to_nfa(graph)

    expected_nfa = NondeterministicFiniteAutomaton()
    expected_nfa.add_start_state(State(0))
    expected_nfa.add_final_state(State(0))
    expected_nfa.add_transition(State(0), Symbol("0"), State(0))

    assert nfa_from_graph.is_equivalent_to(expected_nfa)