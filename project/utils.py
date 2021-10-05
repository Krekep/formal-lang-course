"""
A set of methods for working with a graph.
"""

from typing import Tuple, Dict, Set
import cfpq_data
import networkx as nx

import pyformlang
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
    EpsilonNFA,
    State,
    FiniteAutomaton,
)
from pyformlang.regular_expression import Regex
import scipy
from scipy import sparse

__all__ = [
    "get_graph_info",
    "create_two_cycle_graph",
    "regex_to_nfa",
    "nfa_to_minimal_dfa",
    "regex_to_dfa",
    "graph_to_nfa",
    "rpq",
]

from project.AutomatonMatrix import AutomatonSetOfMatrix


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
    available_nodes = set()
    for node in graph.nodes:
        nfa.states.add(State(node))
        available_nodes.add(node)

    for node_from, node_to in graph.edges():
        edge_label = graph.get_edge_data(node_from, node_to)[0]["label"]
        nfa.add_transition(node_from, edge_label, node_to)

    if not start_vertices:
        for state in nfa.states:
            nfa.add_start_state(state)
    else:
        for start_vertica in start_vertices:
            t = int(start_vertica)
            if t not in available_nodes:
                raise Exception(f"Node {t} does not exists in specified graph")
            nfa.add_start_state(State(t))

    if not finish_vertices:
        for state in nfa.states:
            nfa.add_final_state(state)
    else:
        for finish_vertica in finish_vertices:
            t = int(finish_vertica)
            if t not in available_nodes:
                raise Exception(f"Node {t} does not exists in specified graph")
            nfa.add_final_state(State(t))

    return nfa


def rpq(
    graph: nx.MultiDiGraph,
    regex: str,
    start_vertices: set = None,
    final_vertices: set = None,
) -> set:
    """
    Get set of reachable pairs of graph vertices
    Parameters
    ----------
    graph
        Input Graph
    regex
        Input regular expression
    start_vertices
        Start vertices for graph
    final_vertices
        Final vertices for graph

    Returns
    -------
    set
        Set of reachable pairs of graph vertices
    """
    regex_automaton_matrix = AutomatonSetOfMatrix.from_automaton(regex_to_dfa(regex))
    graph_automaton_matrix = AutomatonSetOfMatrix.from_automaton(
        graph_to_nfa(graph, start_vertices, final_vertices)
    )
    intersected_automaton = graph_automaton_matrix.intersect(regex_automaton_matrix)
    tc_matrix = intersected_automaton.get_transitive_closure()
    res = set()

    for s_from, s_to in zip(*tc_matrix.nonzero()):
        if (
            s_from in intersected_automaton.start_states
            and s_to in intersected_automaton.final_states
        ):
            res.add(
                (
                    s_from // regex_automaton_matrix.num_states,
                    s_to // regex_automaton_matrix.num_states,
                )
            )

    return res
