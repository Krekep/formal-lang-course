from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
)
from pyformlang.regular_expression import Regex


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
    Building a minimal deterministic state automaton from a non-deterministic state automaton.

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
    Building a minimal non-deterministic state automaton from a regular expression.

    Parameters
    ----------
    regex: str
        Regular expression in string format.

    Returns
    -------
    DeterministicFiniteAutomaton
        Deterministic Finite Automaton, which is equivalent to given regex expression.
    """

    nfa = regex_to_nfa(regex)
    dfa = nfa_to_minimal_dfa(nfa)
    return dfa


def replace_nfa_states(
    nfa: NondeterministicFiniteAutomaton,
    start_states: set = None,
    final_states: set = None,
) -> NondeterministicFiniteAutomaton:
    new_nfa = nfa.copy()

    if start_states:
        for state in nfa.start_states:
            new_nfa.remove_start_state(state)
        for state in start_states:
            new_nfa.add_start_state(state)

    if final_states:
        for state in nfa.final_states:
            new_nfa.remove_final_state(state)
        for state in final_states:
            new_nfa.add_final_state(state)

    return new_nfa


def add_nfa_states(
    nfa: NondeterministicFiniteAutomaton,
    start_states: set = None,
    final_states: set = None,
) -> NondeterministicFiniteAutomaton:
    new_nfa = nfa.copy()

    for state in start_states:
        new_nfa.add_start_state(state)
    for state in final_states:
        new_nfa.add_final_state(state)

    return new_nfa
