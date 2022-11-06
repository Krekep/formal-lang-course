import pytest
from pyformlang.cfg import CFG

from project.cyk import cyk


@pytest.mark.parametrize(
    "cfg, word, result",
    [
        (
            CFG.from_text(
                """
                S -> A B C D E
                A -> a | epsilon
                B -> b
                C -> c
                D -> A
                E -> epsilon
                """
            ),
            "abc",
            True,
        ),
        (
            CFG.from_text(
                """
                S -> a b c D
                D -> E
                E -> d
                """
            ),
            "abc",
            False,
        ),
        (
            CFG.from_text(
                """
                S -> A B
                A -> a b b c c c | c c c b b a | a a
                B -> X | Y
                X -> $ | x x x
                Y -> $ | y y y
                """
            ),
            "abbccc",
            True,
        ),
        (
            CFG.from_text(
                """
                S -> A
                A -> a
                B -> b
                """
            ),
            "",
            False,
        ),
        (
            CFG.from_text(
                """
                S -> a S b | epsilon
                """
            ),
            "",
            True,
        ),
        (
            CFG.from_text(
                """
                S -> a S b | epsilon
                """
            ),
            "aabb",
            True,
        ),
    ],
)
def test_check_word_in_cfg_language(cfg: CFG, word: str, result: bool):
    assert result == cyk(word, cfg)
