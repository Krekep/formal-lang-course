import networkx as nx

from project.automaton_matrix import AutomatonSetOfMatrix
from project.fa_utils import regex_to_dfa
from project.graph_utils import graph_to_nfa


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
