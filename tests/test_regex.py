from project import utils
from pyformlang.finite_automaton import Symbol


def test_regex_to_dfa():
    regex = "11(10)*"
    dfa = utils.regex_to_dfa(regex)
    assert dfa.is_deterministic()


def test_regex_to_nfa():
    regex = "11(10)*"
    nfa = utils.regex_to_nfa(regex)
    assert not nfa.is_deterministic()


def test_regex_to_dfa_language_accept():
    regex = "(1 0) | (1 1) | (0 1) | (0 1 0 1)*"
    language = [
        [],
        [Symbol("1"), Symbol("0")],
        [Symbol("1"), Symbol("1")],
        [Symbol("0"), Symbol("1")],
        [Symbol("0"), Symbol("1"), Symbol("0"), Symbol("1")],
    ]
    dfa = utils.regex_to_dfa(regex)
    for word in language:
        assert dfa.accepts(word)


def test_regex_to_dfa_language_non_accept():
    regex = "(1 0) | (1 1) | (0 1) | (0 1 0 1)"
    language = [
        [Symbol("0"), Symbol("0")],
        [Symbol("1"), Symbol("1"), Symbol("1")],
        [Symbol("0"), Symbol("1"), Symbol("1")],
        [Symbol("1"), Symbol("1"), Symbol("0"), Symbol("1")],
    ]
    dfa = utils.regex_to_dfa(regex)
    for word in language:
        assert not dfa.accepts(word)
