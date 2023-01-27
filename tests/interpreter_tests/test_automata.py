from interprert_token import interpret_token

from project.fa_utils import regex_to_dfa

import pytest


@pytest.mark.parametrize(
    "lhs, op, rhs, expected",
    [
        ('"l1" & "l1"', "&", '"l1" | "l1"', '"l1"'),
        ('"l1" | "l2"', "|", '"l2" | "l3"', '"l1" | "l2" | "l3"'),
    ],
)
def test_FA_FA_intersection(lhs, op, rhs, expected):
    expr = lhs + " " + op + " " + rhs
    actual = interpret_token(expr, "expr")
    expected = regex_to_dfa(expected)
    assert actual.nfa.is_equivalent_to(expected)
