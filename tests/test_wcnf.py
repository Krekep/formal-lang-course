import pytest
from pyformlang.cfg import CFG

from project.cfg_utils import cfg_to_wcnf


@pytest.mark.parametrize(
    "cfg, expected, contained_word",
    [
        (
            """
                S -> S S | epsilon
            """,
            """
                S -> S S
                S -> epsilon
            """,
            {
                True: [""],
                False: ["  ", "S"],
            },
        ),
        (
            """
                S -> A
                A -> B
                B -> b
            """,
            """
                S -> b
            """,
            {
                True: ["b"],
                False: ["", "a", "bb"],
            },
        ),
        (
            """
                S -> a b c d e
            """,
            """
                S -> A B1
                B1 -> B2 C1
                C1 -> C2 D1
                D1 -> D2 E
                A -> a
                B2 -> b
                C2 -> c
                D2 -> d
                E -> e 
            """,
            {
                True: ["abcde"],
                False: ["abcd", "", "bb"],
            },
        ),
        (
            """
                S -> a S b N c
                S -> epsilon
                N -> epsilon
                N -> N N
                N -> d e f g h
            """,
            """
                S -> epsilon
                N -> epsilon
                N -> N N
                S -> A C4
                A -> a
                N -> D C1
                D -> d
                C1 -> E C2
                E -> e
                C2 -> F C3
                F -> f
                C3 -> G H
                G -> g
                H -> h
                C4 -> S C5
                C5 -> B C6
                B -> b
                C6 -> N C
                C -> c
            """,
            {
                True: ["", "abc", "aabcbc", "aabcbdefghc"],
                False: ["aabcb", "ab", "bb", "defgh"],
            },
        ),
    ],
)
def test_wcnf(cfg, expected, contained_word):
    actual = cfg_to_wcnf(cfg)
    wcnf_expected = CFG.from_text(expected)
    assert actual.start_symbol == wcnf_expected.start_symbol
    assert all(
        actual.contains(w) and wcnf_expected.contains(w) for w in contained_word[True]
    ) and all(
        not actual.contains(w) and not wcnf_expected.contains(w) for w in contained_word[False]
    )
    assert len(actual.productions) == len(wcnf_expected.productions)


@pytest.mark.parametrize(
    "cfg, expected_eps_vars",
    [
        (
            """
                    S -> S S | epsilon
                """,
            {"S"},
        ),
        (
            """
                    S -> S S | A
                    A -> B | epsilon
                    B -> epsilon
                """,
            {"S"},
        ),
        (
            """
                    S -> A a | S a
                    A -> epsilon
                    B -> epsilon
                """,
            {"A"},
        ),
    ],
)
def test_eps_generating(cfg, expected_eps_vars):
    wcnf = cfg_to_wcnf(cfg)
    actual_eps_vars = {p.head.value for p in wcnf.productions if not p.body}
    assert actual_eps_vars == expected_eps_vars


@pytest.mark.parametrize(
    "cfg, contained_words",
    [
        (
            """
                    S -> epsilon
                    A -> a | b | c | d
                """,
            {
                True: [""],
                False: ["a", "b", "c", "d"],
            },
        ),
        (
            """
                    S -> a S b S
                    S -> epsilon
                """,
            {
                True: ["", "aaabbb", "abaabb", "ababab"],
                False: ["abc", "aa", "bb", "ababa"],
            },
        ),
    ],
)
def test_generated_words(cfg, contained_words):
    cfg = CFG.from_text(cfg)
    wcnf = cfg_to_wcnf(cfg)
    assert all(
        wcnf.contains(w) and cfg.contains(w) for w in contained_words[True]
    ) and all(
        not wcnf.contains(w) and not cfg.contains(w) for w in contained_words[False]
    )
