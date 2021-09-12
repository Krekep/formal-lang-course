"""
A set of methods for working with a graph.
"""

from typing import Tuple
import cfpq_data
import networkx as nx
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
)
from pyformlang.regular_expression import Regex

__all__ = ["regex_to_nfa", "nfa_to_minimal_dfa", "regex_to_dfa"]


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
    dfa.minimize()
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
