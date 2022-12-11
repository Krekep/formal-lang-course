from pyformlang.finite_automaton import State, Symbol
from scipy.sparse import csr_matrix
from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Variable, Terminal

from project.automaton_matrix import AutomatonSetOfMatrix
from project.cfg_utils import cfg_to_wcnf, read_grammar_to_str, read_cfg
from project.ecfg import ECFG
from project.graph_utils import graph_to_nfa
from project.manager import get_graph

__all__ = ["cfpq_by_hellings", "cfpq_by_matrix", "cfpq_by_tensor", "cfpq"]

from project.rsm import RSM


def hellings(
    graph: MultiDiGraph | str,
    cfg: CFG | str,
    **kwargs,
) -> set[tuple]:
    """
    Constrained transitive closure by Hellings algorithm

    Parameters
    ----------
    graph: MultiDiGraph | str
        Graph passed as MultiDiGraph object or graph name from cfpq_data dataset
    cfg: CFG | str
        Grammar passed as CFG object, string representation or path to file with grammar
    start_symbol: str
        Start non-terminal for context-free grammar in case grammar is not CFG object
    grammar_in_file: bool
        Is grammar passed as path to file with grammar

    Returns
    -------
    result: set[tuple]
        Set of triples (start vertex, non-terminal symbol, final vertex)
    """

    grammar_in_file = kwargs.get("grammar_in_file", False)
    start_symbol = kwargs.get("start_symbol", "S")

    # transform graph and grammar
    if grammar_in_file:
        cfg = read_grammar_to_str(cfg)

    if isinstance(cfg, str):
        cfg = read_cfg(cfg, start_symbol)

    if isinstance(graph, str):
        graph = get_graph(graph)

    cfg = cfg_to_wcnf(cfg)

    # split productions in 3 groups
    eps_prods = set()  # A -> epsilon
    term_prods = {}  # A -> a
    var_prods = {}  # A -> B C
    for p in cfg.productions:
        if not p.body:
            eps_prods.add(p.head)
        elif len(p.body) == 1:
            t = p.body[0]
            term_prods.setdefault(p.head, set()).add(t)
        elif len(p.body) == 2:
            v1, v2 = p.body
            var_prods.setdefault(p.head, set()).add((v1, v2))

    # prepare result
    result = set()

    for v, u, data in graph.edges(data=True):
        label = data["label"]
        for var in term_prods:
            if Terminal(label) in term_prods[var]:
                result.add((v, var, u))

    for node in graph.nodes:
        for var in eps_prods:
            result.add((node, var, node))

    # helling
    queue = result.copy()
    while len(queue) > 0:
        s, var, f = queue.pop()

        temp = set()

        for triple in result:
            if triple[-1] == s:
                for curr_var in var_prods:
                    if (triple[1], var) in var_prods[curr_var] and (
                        triple[0],
                        curr_var,
                        f,
                    ) not in result:
                        queue.add((triple[0], curr_var, f))
                        temp.add((triple[0], curr_var, f))
            if triple[0] == f:
                for curr_var in var_prods:
                    if (var, triple[1]) in var_prods[curr_var] and (
                        s,
                        curr_var,
                        triple[-1],
                    ) not in result:
                        queue.add((s, curr_var, triple[-1]))
                        temp.add((s, curr_var, triple[-1]))

        result = result.union(temp)

    return result


def matrix_based(
    graph: MultiDiGraph | str,
    cfg: CFG | str,
    **kwargs,
) -> set[tuple]:
    """
    Transitive closure based on Matrix Multiplication algorithm

     Parameters
    ----------
    graph: MultiDiGraph | str
        Graph passed as MultiDiGraph object or graph name from cfpq_data dataset
    cfg: CFG | str
        Grammar passed as CFG object, string representation or path to file with grammar
    start_symbol: str
        Start non-terminal for context-free grammar in case grammar is not CFG object
    grammar_in_file: bool
        Is grammar passed as path to file with grammar

    Returns
    -------
    result: set[tuple]
        Set of triples (start vertex, non-terminal symbol, final vertex)
    """

    grammar_in_file = kwargs.get("grammar_in_file", False)
    start_symbol = kwargs.get("start_symbol", "S")

    # transform graph and grammar
    if grammar_in_file:
        cfg = read_grammar_to_str(cfg)

    if isinstance(cfg, str):
        cfg = read_cfg(cfg, start_symbol)

    if isinstance(graph, str):
        graph = get_graph(graph)

    cfg = cfg_to_wcnf(cfg)

    # split productions in 3 groups
    eps_prods = set()  # A -> epsilon
    term_prods = {}  # A -> a
    var_prods = {}  # A -> B C
    for p in cfg.productions:
        if not p.body:
            eps_prods.add(p.head)
        elif len(p.body) == 1:
            t = p.body[0]
            term_prods.setdefault(p.head, set()).add(t)
        elif len(p.body) == 2:
            v1, v2 = p.body
            var_prods.setdefault(p.head, set()).add((v1, v2))

    # prepare adjacency matrix
    nodes_num = graph.number_of_nodes()
    nodes = {vertex: i for i, vertex in enumerate(graph.nodes)}
    nodes_reversed = {i: vertex for i, vertex in enumerate(graph.nodes)}
    matrices = {
        v: csr_matrix((nodes_num, nodes_num), dtype=bool) for v in cfg.variables
    }

    # A -> terminal
    for v, u, data in graph.edges(data=True):
        label = data["label"]
        i = nodes[v]
        j = nodes[u]
        for var in term_prods:
            if Terminal(label) in term_prods[var]:
                matrices[var][i, j] = True

    # A -> espilon loops
    for var in eps_prods:
        for i in range(nodes_num):
            matrices[var][i, i] = True

    # A -> B C
    changed = True
    while changed:
        changed = False
        for head in var_prods:
            for body_b, body_c in var_prods[head]:
                old_nnz = matrices[head].nnz
                matrices[head] += matrices[body_b] @ matrices[body_c]
                new_nnz = matrices[head].nnz
                changed = old_nnz != new_nnz

    return {
        (nodes_reversed[v], var, nodes_reversed[u])
        for var, matrix in matrices.items()
        for v, u in zip(*matrix.nonzero())
    }


def tensor_based(
    graph: MultiDiGraph | str,
    cfg: CFG | str,
    **kwargs,
) -> set[tuple]:
    """
    Transitive closure based on Tensor algorithm

     Parameters
    ----------
    graph: MultiDiGraph | str
        Graph passed as MultiDiGraph object or graph name from cfpq_data dataset
    cfg: CFG | str
        Grammar passed as CFG object, string representation or path to file with grammar
    start_symbol: str
        Start non-terminal for context-free grammar in case grammar is not CFG object
    grammar_in_file: bool
        Is grammar passed as path to file with grammar

    Returns
    -------
    result: set[tuple]
        Set of triples (start vertex, non-terminal symbol, final vertex)
    """

    grammar_in_file = kwargs.get("grammar_in_file", False)
    start_symbol = kwargs.get("start_symbol", "S")

    # transform graph and grammar
    if grammar_in_file:
        cfg = read_grammar_to_str(cfg)

    if isinstance(cfg, str):
        cfg = read_cfg(cfg, start_symbol)

    if isinstance(graph, str):
        graph = get_graph(graph)

    g_matrix = AutomatonSetOfMatrix.from_automaton(graph_to_nfa(graph))
    rsm = RSM.from_ecfg((ECFG.from_cfg(cfg)))
    rsm_matrix = AutomatonSetOfMatrix.from_rsm(rsm)
    rsm_idx_to_state = {i: s for s, i in rsm_matrix.state_indices.items()}

    for var in cfg.get_nullable_symbols():
        if var not in g_matrix.bool_matrices.keys():
            g_matrix.bool_matrices[var] = csr_matrix(
                (g_matrix.num_states, g_matrix.num_states), dtype=bool
            )
        for i in range(g_matrix.num_states):
            g_matrix.bool_matrices[var][i, i] = True

    intersection = rsm_matrix.intersect(g_matrix)
    tc = intersection.get_transitive_closure()

    prev_nnz = tc.nnz
    new_nnz = 0

    while prev_nnz != new_nnz:
        for i, j in zip(*tc.nonzero()):
            rsm_i = i // g_matrix.num_states
            rsm_j = j // g_matrix.num_states

            graph_i = i % g_matrix.num_states
            graph_j = j % g_matrix.num_states

            s, f = rsm_idx_to_state[rsm_i], rsm_idx_to_state[rsm_j]
            var, _ = s.value

            if s in rsm_matrix.start_states and f in rsm_matrix.final_states:
                if var not in g_matrix.bool_matrices.keys():
                    g_matrix.bool_matrices[var] = csr_matrix(
                        (g_matrix.num_states, g_matrix.num_states), dtype=bool
                    )
                g_matrix.bool_matrices[var][graph_i, graph_j] = True

        tc = rsm_matrix.intersect(g_matrix).get_transitive_closure()

        prev_nnz, new_nnz = new_nnz, tc.nnz

    return {
        (u, label, v)
        for label, bm in g_matrix.bool_matrices.items()
        for u, v in zip(*bm.nonzero())
    }


def cfpq_by_hellings(
    cfg: CFG,
    graph: MultiDiGraph,
    start_symbol: Variable = Variable("S"),
    start_nodes: set[any] = None,
    final_nodes: set[any] = None,
    **kwargs,
) -> set[tuple[any, any]]:
    """
    Performs context-free path querying in graph with given context-free grammar via Hellings algorithm

    Parameters
    ----------
    cfg: CFG
        Input grammar
    graph: MultiDiGraph
        Graph
    start_symbol: Varibale
        Start non-terminal to make query
    start_nodes: set
        Start nodes in graph
    final_nodes: set
        Final nodes in graph

    Returns
    -------
        Tuple with nodes satisfying cfpq
    """
    return cfpq(cfg, graph, start_symbol, start_nodes, final_nodes, hellings, **kwargs)


def cfpq_by_matrix(
    cfg: CFG,
    graph: MultiDiGraph,
    start_symbol: Variable = Variable("S"),
    start_nodes: set[any] = None,
    final_nodes: set[any] = None,
    **kwargs,
) -> set[tuple[any, any]]:
    """
    Performs context-free path querying in graph with given context-free grammar via Matrix Multiplication

    Parameters
    ----------
    cfg: CFG
        Input grammar
    graph: MultiDiGraph
        Graph
    start_symbol: Varibale
        Start non-terminal to make query
    start_nodes: set
        Start nodes in graph
    final_nodes: set
        Final nodes in graph

    Returns
    -------
        Tuple with nodes satisfying cfpq
    """
    return cfpq(
        cfg, graph, start_symbol, start_nodes, final_nodes, matrix_based, **kwargs
    )


def cfpq_by_tensor(
    cfg: CFG,
    graph: MultiDiGraph,
    start_symbol: Variable = Variable("S"),
    start_nodes: set[any] = None,
    final_nodes: set[any] = None,
    **kwargs,
) -> set[tuple[any, any]]:
    """
    Performs context-free path querying in graph with given context-free grammar via Tensor based algorithm

    Parameters
    ----------
    cfg: CFG
        Input grammar
    graph: MultiDiGraph
        Graph
    start_symbol: Varibale
        Start non-terminal to make query
    start_nodes: set
        Start nodes in graph
    final_nodes: set
        Final nodes in graph

    Returns
    -------
        Tuple with nodes satisfying cfpq
    """
    return cfpq(
        cfg, graph, start_symbol, start_nodes, final_nodes, tensor_based, **kwargs
    )


def cfpq(
    cfg: CFG,
    graph: MultiDiGraph,
    start_symbol: Variable = Variable("S"),
    start_nodes: set[any] = None,
    final_nodes: set[any] = None,
    algorithm: callable = hellings,
    **kwargs,
) -> set[tuple[any, any]]:
    """
    Performs context-free path querying in graph with given context-free grammar and algorithm

    Parameters
    ----------
    cfg: CFG
        Input grammar
    graph: MultiDiGraph
        Graph
    start_symbol: Varibale
        Start non-terminal to make query
    start_nodes: set
        Start nodes in graph
    final_nodes: set
        Final nodes in graph
    algorithm: callable
        Algorithm to perform context-free path query

    Returns
    -------
        Tuple with nodes satisfying cfpq
    """

    # default config
    args = {
        "grammar_in_file": False,
        "start_symbol": start_symbol.value,
    }

    for kw in kwargs:
        args[kw] = kwargs[kw]

    if start_nodes is None:
        start_nodes = set(graph.nodes)

    if final_nodes is None:
        final_nodes = set(graph.nodes)

    result = algorithm(graph, cfg, **args)
    ans = set(
        [
            (u, v)
            for u, var, v in result
            if var == start_symbol and u in start_nodes and v in final_nodes
        ]
    )
    return ans
