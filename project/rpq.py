from __future__ import annotations

import networkx as nx

from project.automaton_matrix import AutomatonSetOfMatrix
from project.fa_utils import regex_to_dfa
from project.graph_utils import graph_to_nfa

from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from scipy import sparse
import numpy as np

__all__ = ["rpq", "bfs_rpq"]


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


def _build_adj_empty_matrix(g: nx.MultiDiGraph) -> sparse.csr_matrix:
    """
    Build empty adjacency matrix for passed graph

    Parameters
    ----------
    g: nx.MultiDiGraph
        Input graph

    Returns
    -------
    adj_m: sparse.csr_matrix
        Adjacency matrix
    """

    return sparse.csr_matrix(
        (len(g.nodes), len(g.nodes)),
        dtype=bool,
    )


def _build_direct_sum(
    r: DeterministicFiniteAutomaton, g: nx.MultiDiGraph
) -> dict[sparse.csr_matrix]:
    """
    Build direct sum of boolean matrix decomposition dfa and graph

    Parameters
    ----------
    r: DeterministicFiniteAutomaton
        Input dfa
    g: nx.MultiDiGraph
        Input graph

    Returns
    -------
    d: dict[sparse.csr_matrix]
        Result of direct sum
    """

    d = {}

    r_matrix = AutomatonSetOfMatrix.from_automaton(r)
    g_matrix = AutomatonSetOfMatrix.from_automaton(graph_to_nfa(g))

    r_labels = set(r_matrix.bool_matrices.keys())
    g_labels = set(g_matrix.bool_matrices.keys())
    labels = r_labels.intersection(g_labels)

    r_size = r_matrix.num_states
    g_size = g_matrix.num_states
    for label in labels:
        left_up_matrix = r_matrix.bool_matrices[label]
        right_up_matrix = sparse.csr_matrix(
            (r_size, g_size),
            dtype=bool,
        )
        left_down_matrix = sparse.csr_matrix(
            (g_size, r_size),
            dtype=bool,
        )
        right_down_matrix = g_matrix.bool_matrices[label]
        d[label] = sparse.vstack(
            [
                sparse.hstack(
                    [left_up_matrix, right_up_matrix], dtype=bool, format="csr"
                ),
                sparse.hstack(
                    [left_down_matrix, right_down_matrix], dtype=bool, format="csr"
                ),
            ],
            dtype=bool,
            format="csr",
        )

    return d


def _create_masks(
    r: DeterministicFiniteAutomaton, g: nx.MultiDiGraph
) -> sparse.csr_matrix:
    """
    Create M matrix

    Parameters
    ----------
    r: DeterministicFiniteAutomaton
        Input dfa
    g: nx.MultiDiGraph
        Input graph

    Returns
    -------
    m: sparse.csr_matrix

    """

    r_size = len(r.states)
    g_size = len(g.nodes)

    id = sparse.identity(r_size, dtype=bool, format="csr")
    front = sparse.csr_matrix(
        (r_size, g_size),
        dtype=bool,
    )
    m = sparse.hstack([id, front], dtype=bool, format="csr")

    return m


def _set_start_verts(m: sparse.csr_matrix, v_src: set) -> sparse.csr_matrix:
    """
    Add start vertices to right part of M matrix

    Parameters
    ----------
    m: sparse.csr_matrix
        M matrix
    v_src: set
        Start vertices set

    Returns
    -------
    m_new: sparse.csr_matrix
        Updated M matrix
    """
    r_size = m.get_shape()[0]
    for i in range(r_size):
        for start_v in v_src:
            m[i, r_size + start_v] = 1

    return m


def _get_graph_labels(g: nx.MultiDiGraph) -> set[str]:
    """
    Extract graph labels from edges

    Parameters
    ----------
    g: nx.MultiDiGraph
        Input graph

    Returns
    -------
    labels: set[str]
        Extracted labels
    """

    labels = set()
    for node_from, node_to in g.edges():
        labels.add(g.get_edge_data(node_from, node_to)[0]["label"])

    return labels


def _extract_left_submatrix(m: sparse.csr_matrix) -> sparse.csr_matrix:
    """
    Extract left part of M matrix --- identity matrix

    Parameters
    ----------
    m: sparse.csr_matrix
        M matrix

    Returns
    -------
    m: sparse.csr_matrix
        Identity matrix
    """

    extr_size = m.shape[0]
    extr_columns = np.arange(extr_size)
    return m[:, extr_columns]


def _extract_right_submatrix(m: sparse.csr_matrix) -> sparse.csr_matrix:
    """
    Extract right part of M matrix --- front

    Parameters
    ----------
    m: sparse.csr_matrix
        M matrix

    Returns
    -------
    m: sparse.csr_matrix
        Front
    """

    extr_size = m.shape[0]
    extr_columns = np.arange(extr_size, m.shape[1])
    return m[:, extr_columns]


def _transform_front_part(front_part: sparse.csr_array) -> sparse.csr_matrix:
    """
    Transform another front to right form of M matrix. Left submatrix is identity matrix

    Parameters
    ----------
    front_part: sparse.csr_matrix
        Input matrix

    Returns
    -------
    m: sparse.csr_matrix
        Transformed matrix
    """

    t = _extract_left_submatrix(front_part)
    m_new = sparse.csr_matrix(
        front_part.shape,
        dtype=bool,
    )
    nnz_row, nnz_col = t.nonzero()
    for i in range(len(nnz_col)):
        row = front_part.getrow(nnz_row[i])
        m_new[nnz_col[i], :] = row
    return m_new


def _reduce_to_vector(m: sparse.csr_matrix) -> sparse.csr_matrix:
    """
    Reduce matrix to vector

    Parameters
    ----------
    m: sparse.csr_matrix
        Input matrix

    Returns
    -------
    v: sparse.csr_matrix
        Reduced vector
    """
    shape = m.shape
    v = sparse.csr_matrix(
        (1, shape[1]),
        dtype=bool,
    )
    for row in range(shape[0]):
        v += m.getrow(row)

    return v


def _bfs_based_rpq(
    r: DeterministicFiniteAutomaton, g: nx.MultiDiGraph, v_src: set
) -> sparse.csr_matrix:
    """

    Parameters
    ----------
    r: DeterministicFiniteAutomaton
        Input dfa
    g: nx.MultiDiGraph
        Input graph
    v_src: set
        Start vertices set

    Returns
    -------
    p: sparse.csr_matrix
        Adjacency matrix where (i, j) = True if `i` in v_src and `j` is reachable from v_src
    """

    p = _build_adj_empty_matrix(g)
    d = _build_direct_sum(r, g)
    init_m = _create_masks(r, g)
    init_m = _set_start_verts(init_m, v_src)

    labels = r.symbols.intersection(_get_graph_labels(g))

    old_nnz = 0
    new_nnz = init_m.nnz
    first_iteration = True
    m_new = sparse.csr_matrix(
        init_m.shape,
        dtype=bool,
    )

    while old_nnz != new_nnz:
        old_nnz = new_nnz
        for label in labels:
            m_temp = init_m.dot(d[label]) if first_iteration else m_new.dot(d[label])
            m_new = m_new + _transform_front_part(m_temp)

        reachable = _extract_right_submatrix(m_new)
        v = _reduce_to_vector(reachable)
        for k in v_src:
            w = p.getrow(k)
            p[k, :] = v + w

        first_iteration = False
        new_nnz = m_new.nnz
    return p


def bfs_rpq(
    graph: nx.MultiDiGraph,
    regex: str,
    start_vertices: set = None,
    final_vertices: set = None,
    separated: bool = False,
) -> set[tuple[int, frozenset] | frozenset]:
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
    separated
        Process for each start vertex or for set of start vertices

    Returns
    -------
    set
        Set of reachable pairs of graph vertices
    """
    regex_automaton = regex_to_dfa(regex)
    rpq_result = _bfs_based_rpq(regex_automaton, graph, start_vertices)

    if final_vertices is None:
        final_vertices = set()
        for node in graph.nodes:
            final_vertices.add(node)

    res = set()
    if separated:
        for s_v in start_vertices:
            temp = list()
            row = rpq_result.getrow(s_v)
            for vertex in row.indices:
                if vertex in final_vertices:
                    temp.append(vertex)
            res.add((s_v, frozenset(temp)))
    else:
        reachable_vertices = list()
        for s_v in start_vertices:
            row = rpq_result.getrow(s_v)
            for vertex in row.indices:
                if vertex in final_vertices:
                    reachable_vertices.append(vertex)
        res.add(frozenset(reachable_vertices))

    return res
