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
    State, FiniteAutomaton,
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
    "automaton_to_matrix",
    "matrix_to_automaton",
    "rpq",
    "intersect",
    "get_transitive_closure"
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


def automaton_to_matrix(automaton: FiniteAutomaton) -> Tuple[Dict, int, Set[State], Set[State], Dict]:
    """
    Transform automaton to set of labeled boolean matrix
    Parameters
    ----------
    automaton
        Automaton for transforming

    Returns
    -------
    Tuple[Dict, int, Set[State], Set[State], Dict]
        Set of labeled matrix, size of matrix, set of start states, state of final states, map of state and their indices
    """
    matrix = {}
    num_states = len(automaton.states)
    start_states = automaton.start_states
    final_states = automaton.final_states
    state_indices = {state: idx for idx, state in enumerate(automaton.states)}

    for s_from, trans in automaton.to_dict().items():
        for label, states_to in trans.items():
            if not isinstance(states_to, set):
                states_to = {states_to}
            for s_to in states_to:
                idx_from = state_indices[s_from]
                idx_to = state_indices[s_to]
                if label not in matrix.keys():
                    matrix[label] = sparse.csr_matrix(
                        (num_states, num_states), dtype=bool
                    )
                matrix[label][idx_from, idx_to] = True

    return matrix, num_states, start_states, final_states, state_indices


def matrix_to_automaton(matrix: Dict, start_states: Set[State],
                        final_states: Set[State]) -> NondeterministicFiniteAutomaton:
    """
    Transform set of labeled boolean matrix to automaton.
    Parameters
    ----------
    matrix: Dict
        Set of boolean matrix with label as key
    start_states
        Start states for automaton
    final_states
        Final states for automaton

    Returns
    -------
    NondeterministicFiniteAutomaton
        Resulting automaton
    """

    automaton = NondeterministicFiniteAutomaton()
    for label in matrix.keys():
        for s_from, s_to in zip(*matrix[label].nonzero()):
            automaton.add_transition(s_from, label, s_to)

    for state in start_states:
        automaton.add_start_state(State(state))

    for state in final_states:
        automaton.add_final_state(State(state))

    return automaton


def get_transitive_closure(matrix: sparse.csr_matrix) -> sparse.csr_matrix:
    """
    Get transitive closure of sparse.csr_matrix
    Parameters
    ----------
    matrix
        Matrix for transitive closure
    Returns
    -------
        Transitive closure
    """
    prev_nnz = matrix.nnz
    new_nnz = 0

    while prev_nnz != new_nnz:
        matrix += matrix @ matrix
        prev_nnz, new_nnz = new_nnz, matrix.nnz

    return matrix


def intersect(first: FiniteAutomaton, second: FiniteAutomaton) -> Tuple[Dict, int, Set[State], Set[State], Dict]:
    """
    Get intersection of two automatons
    Parameters
    ----------
    first
        First automaton
    second
        Second automaton

    Returns
    -------
    Tuple[Dict, int, Set[State], Set[State], Dict]
        Set of labeled matrix, size of matrix, set of start states, state of final states, map of state and their indices
    """
    first_matrix, first_size, first_start, first_final, first_states = automaton_to_matrix(first)
    second_matrix, second_size, second_start, second_final, second_states = automaton_to_matrix(second)
    res_matrix = {}
    res_size = first_size * second_size
    res_states = {}
    res_start = set()
    res_final = set()
    common_labels = set(first_matrix.keys()).union(second_matrix.keys())

    for label in common_labels:
        if label not in first_matrix.keys():
            first_matrix[label] = sparse.csr_matrix((first_size, first_size), dtype=bool)
        if label not in second_matrix.keys():
            second_matrix[label] = sparse.csr_matrix((second_size, second_size), dtype=bool)

    for label in common_labels:
        res_matrix[label] = sparse.kron(
            first_matrix[label], second_matrix[label], format="csr"
        )

    for f_s, f_s_i in first_states.items():
        for s_s, s_s_i in second_states.items():
            new_state = new_state_idx = f_s_i * second_size + s_s_i
            res_states[new_state] = new_state_idx

            if f_s in first_start and s_s in second_start:
                res_start.add(new_state)

            if f_s in first_final and s_s in second_final:
                res_final.add(new_state)

    return res_matrix, res_size, res_start, res_final, res_states


def rpq(graph: nx.MultiDiGraph,
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
    regex_dfa = regex_to_dfa(regex)

    intersected_matrix, intersected_size, intersected_start, intersected_final, intersected_states = intersect(
        graph_to_nfa(graph, start_vertices, final_vertices), regex_dfa)
    tc_matrix = sparse.csr_matrix((intersected_size, intersected_size), dtype=bool)
    for label in intersected_matrix.keys():
        tc_matrix += intersected_matrix[label]
    tc_matrix = get_transitive_closure(tc_matrix)
    res = set()

    for s_from, s_to in zip(*tc_matrix.nonzero()):
        if s_from in intersected_start and s_to in intersected_final:
            res.add((s_from // len(regex_dfa.states), s_to // len(regex_dfa.states)))

    return res
