import pytest
from pyformlang.cfg import CFG

from project.cfg_utils import cfg_to_wcnf


@pytest.mark.parametrize(
    "cfg, expected",
    [
        (
            """
                S -> S S | epsilon
            """,
            """
                S -> S S
                S -> epsilon
            """
        ),
        (
            """
                S -> A
                A -> B
                B -> b
            """,
            """
                S -> b
            """
        ),
    ],
)
def test_wcnf(cfg, expected):
    actual = cfg_to_wcnf(cfg)
    wcnf_expected = CFG.from_text(expected)
    assert actual.start_symbol == wcnf_expected.start_symbol
    assert actual.productions == wcnf_expected.productions


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
