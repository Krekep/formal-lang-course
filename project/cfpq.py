import networkx as nx
from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Variable, Terminal

from project.cfg_utils import cfg_to_wcnf

__all__ = ["cfpq"]


def hellings(graph: MultiDiGraph, cfg: CFG) -> set[tuple]:
    """
    Constrained transitive closure by hellings algorithm

    Parameters
    ----------
    graph: MultiDiGraph
    cfg: CFG

    Returns
    -------
    result: set[tuple]
        Set of triple of start vertex, symbols and final vertex
    """

    cfg = cfg_to_wcnf(cfg)

    # split productions in 3 groups
    eps_prods = set()  # A -> epsilon
    term_prods = {}  # A -> a
    var_prods = {}  # A -> B C
    for p in cfg.productions:
        match p.body:
            case []:
                eps_prods.add(p.head)
            case [Terminal() as t]:
                term_prods.setdefault(p.head, set()).add(t)
            case [Variable() as v1, Variable() as v2]:
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


def cfpq(
    cfg: CFG,
    graph: MultiDiGraph,
    start_variable: Variable = Variable("S"),
    start_nodes: list[any] = None,
    final_nodes: list[any] = None,
) -> set[tuple[any, any]]:
    """
    Performs context-free path querying in graph with given context free grammar

    Parameters
    ----------
    cfg: CFG
        Input grammar
    graph: MultiDiGraph
        Graph
    start_variable:
        Start non-terminal to make query
    start_nodes:
        Start nodes in graph
    final_nodes
        Final nodes in graph

    Returns
    -------
        Tuple with nodes satisfying cfpq
    """
    if start_nodes is None:
        start_nodes = list(graph.nodes)

    if final_nodes is None:
        final_nodes = list(graph.nodes)

    hellings_result = hellings(graph, cfg)
    return set(
        [
            (u, v)
            for u, var, v in hellings_result
            if var == start_variable and u in start_nodes and v in final_nodes
        ]
    )
