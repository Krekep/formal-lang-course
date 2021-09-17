"""
A set of methods for working with a graph.
"""

from typing import Tuple
import cfpq_data
import networkx as nx

import pyformlang
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
    EpsilonNFA,
    State,
)
from pyformlang.regular_expression import Regex

__all__ = [
    "get_graph_info",
    "create_two_cycle_graph",
    "regex_to_nfa",
    "nfa_to_minimal_dfa",
    "regex_to_dfa",
    "graph_to_nfa",
]


def get_graph_info(graph: nx.MultiDiGraph) -> Tuple[int, int, set]:
    """
    Gets information about the graph as a tuple of 3 elements -
    the number of nodes, the number of edges, and labels set on the edges.

    Parameters
    ----------
    graph: nx.MultiDiGraph
        Graph from which information is gained

    Returns
    -------
    Tuple[int, int, set]
        Info about graph
    """
    return graph.number_of_nodes(), graph.number_of_edges(), cfpq_data.get_labels(graph)


def create_two_cycle_graph(
    first_vertices: int, second_vertices: int, edge_labels: Tuple[str, str]
) -> nx.MultiDiGraph:
    """
    Create two cycle graph with labels on the edges.

    Parameters
    ----------
    first_vertices: int
        Amount of vertices in the first cycle
    second_vertices: int
        Amount of vertices in the second cycle
    edge_labels: Tuple[str, str]
        Labels for the edges on the first and second cycle

    Returns
    -------
    nx.MultiDiGraph
        Generated graph with two cycles
    """
    return cfpq_data.labeled_two_cycles_graph(
        first_vertices, second_vertices, edge_labels=edge_labels, verbose=False
    )


def regex_to_nfa(regex: str) -> NondeterministicFiniteAutomaton:
    """
    Building a non-deterministic state automaton from a regular expression.

    Parameters
    ----------
    regex: str
        Regular expression.

    Returns
    -------
    NondeterministicFiniteAutomaton
        Non-deterministic Finite Automaton, which is equivalent to given regular expression.
    """

    rgx = Regex(regex)
    nfa = rgx.to_epsilon_nfa()
    return nfa


def nfa_to_minimal_dfa(
    nfa: NondeterministicFiniteAutomaton,
) -> DeterministicFiniteAutomaton:
    """
    Building a non-deterministic state automaton from a regular expression.

    Parameters
    ----------
    nfa: NondeterministicFiniteAutomaton
        Non-deterministic Finite Automaton.

    Returns
    -------
    DeterministicFiniteAutomaton
        Deterministic Finite Automaton, which is equivalent to given non-deterministic Finite Automaton.
    """

    dfa = nfa.to_deterministic()
    dfa = dfa.minimize()
    return dfa


def regex_to_dfa(regex: str) -> DeterministicFiniteAutomaton:
    """
    Building a non-deterministic state automaton from a regular expression.

    Parameters
    ----------
    regex: NondeterministicFiniteAutomaton
        Non-deterministic Finite Automaton.

    Returns
    -------
    DeterministicFiniteAutomaton
        Deterministic Finite Automaton, which is equivalent to given regex expression.
    """

    nfa = regex_to_nfa(regex)
    dfa = nfa_to_minimal_dfa(nfa)
    return dfa


def graph_to_nfa(
    graph: nx.MultiDiGraph, start_vertices: list = None, finish_vertices: list = None
) -> NondeterministicFiniteAutomaton:
    """
    Construction of a non-deterministic automaton from a labeled graph.

    Parameters
    ----------
    graph: nx.MultiDiGraph
        Labeled graph
    start_vertices: nx.MultiDiGraph
        Start vertices
    finish_vertices: nx.MultiDiGraph
        Finish vertices

    Returns
    -------
    NondeterministicFiniteAutomaton
        Resulting non-deterministic automaton
    """

    nfa = NondeterministicFiniteAutomaton()

    for node_from, node_to in graph.edges():
        edge_data = graph.get_edge_data(node_from, node_to)[0]["label"]
        nfa.add_transition(node_from, edge_data, node_to)

    if not start_vertices:
        start_vertices = list(graph.nodes())
    if not finish_vertices:
        finish_vertices = list(graph.nodes())

    for state in start_vertices:
        nfa.add_start_state(State(state))
    for state in finish_vertices:
        nfa.add_final_state(State(state))

    return nfa
