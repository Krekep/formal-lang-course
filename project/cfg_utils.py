from __future__ import annotations

import pyformlang.cfg as c


def cfg_to_wcnf(cfg: str | c.CFG, start: str = None) -> c.CFG:
    """
    Transform context-free-grammar to weak chomsky normal form

    Parameters
    ----------
    cfg: str | CFG
        Grammar
    start: str
        Start symbol

    Returns
    -------
    grammar: CFG
        Grammar in wcnf
    """

    if not isinstance(cfg, c.CFG):
        cfg = read_cfg(cfg, start if start is not None else "S")

    wcnf_cfg = cfg.remove_useless_symbols()
    wcnf_cfg = wcnf_cfg.eliminate_unit_productions()
    wcnf_cfg = wcnf_cfg.remove_useless_symbols()
    wcnf_productions = wcnf_cfg._get_productions_with_only_single_terminals()
    wcnf_productions = wcnf_cfg._decompose_productions(wcnf_productions)

    return c.CFG(start_symbol=wcnf_cfg._start_symbol, productions=set(wcnf_productions))


def read_grammar_to_str(path: str):
    """
    Load grammar from file to string representation

    Parameters
    ----------
    path: str
        Path to file

    Returns
    -------
    grammar: str
        String grammar representation
    """

    with open(path, "r") as f:
        data = f.read()
    return data


def read_cfg(grammar: str, start: str) -> c.CFG:
    """
    Build CFG from string representation of grammar

    Parameters
    ----------
    grammar: str
        String grammar
    start:
        Start symbol for grammar

    Returns
    -------
        Grammar as CFG class
    """

    return c.CFG.from_text(grammar, c.Variable(start))
