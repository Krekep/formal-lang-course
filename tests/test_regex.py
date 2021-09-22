from typing import List, Iterable

import pytest

import project.utils
from project import utils

import pyformlang
from pyformlang import finite_automaton
from pyformlang.finite_automaton import Symbol, DeterministicFiniteAutomaton, State
from pyformlang.regular_expression import MisformedRegexError


def test_regex_to_dfa():
    regex = "1 1 (1 0)*"
    dfa = utils.regex_to_dfa(regex)
    assert dfa.is_deterministic()


def test_regex_to_nfa():
    regex = "1 1 (1 0)*"
    nfa = utils.regex_to_nfa(regex)
    assert not nfa.is_deterministic()


def test_get_min_dfa():
    expected_dfa = DeterministicFiniteAutomaton()

    state_0 = State(0)
    state_1 = State(1)
    state_2 = State(2)

    symbol_a = Symbol("a")
    symbol_b = Symbol("b")
    symbol_c = Symbol("c")

    expected_dfa.add_start_state(state_0)

    expected_dfa.add_final_state(state_2)

    expected_dfa.add_transition(state_0, symbol_a, state_1)
    expected_dfa.add_transition(state_0, symbol_c, state_1)

    expected_dfa.add_transition(state_1, symbol_b, state_2)

    actual_dfa = utils.regex_to_dfa("((a | c) b)")
    assert expected_dfa.is_equivalent_to(actual_dfa)
    assert len(actual_dfa.states) == len(expected_dfa.states)


@pytest.mark.parametrize(
    "regex, expected, unexpected",
    [
        ("", [], [[Symbol("1")], [Symbol("0")]]),
        (
            "(1 0) | (1 1) | (0 1) | (0 1 0 1)*",
            [
                [],
                [Symbol("1"), Symbol("0")],
                [Symbol("1"), Symbol("1")],
                [Symbol("0"), Symbol("1")],
                [Symbol("0"), Symbol("1"), Symbol("0"), Symbol("1")],
                [
                    Symbol("0"),
                    Symbol("1"),
                    Symbol("0"),
                    Symbol("1"),
                    Symbol("0"),
                    Symbol("1"),
                    Symbol("0"),
                    Symbol("1"),
                ],
            ],
            [[Symbol("1")], [Symbol("0")], [Symbol("1"), Symbol("0"), Symbol("1")]],
        ),
        (
            "a*",
            [[], [Symbol("a")], [Symbol("a"), Symbol("a")]],
            [[Symbol("b")], [Symbol("c"), Symbol("d"), Symbol("e")], [Symbol("a*")]],
        ),
    ],
)
def test_regex_to_dfa_accept(
    regex: str,
    expected: List[Iterable[Symbol]],
    unexpected: List[Iterable[Symbol]],
):
    dfa = utils.regex_to_dfa(regex)
    for expected_word in expected:
        assert dfa.accepts(expected_word)
    for unexpected_word in unexpected:
        assert not dfa.accepts(unexpected_word)


def test_exception():
    with pytest.raises(MisformedRegexError):
        utils.regex_to_dfa("*|wrong|*")
