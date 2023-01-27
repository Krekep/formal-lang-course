from interprert_token import interpret_token
from project.grammar.interpreter.my_types.AntlrBool import AntlrBool
from project.grammar.interpreter.exceptions import NotImplementedException

import pytest


@pytest.mark.parametrize(
    "lhs, op, rhs, expected",
    [
        ("true", "&", "false", False),
        ("true", "|", "false", True),
        ("false", "|", "false", False),
    ],
)
def test_binary_or_and(lhs, op, rhs, expected):
    expr = lhs + " " + op + " " + rhs
    assert interpret_token(expr, "expr") == AntlrBool(expected)


@pytest.mark.parametrize(
    "lhs, expected",
    [
        ("true", False),
        ("false", True),
    ],
)
def test_inversion(lhs, expected):
    expr = "not " + lhs
    assert interpret_token(expr, "expr") == AntlrBool(expected)


@pytest.mark.parametrize(
    "lhs, op, rhs",
    [
        ("true", ".", "true"),
        ("true", "*", None),
    ],
)
def test_unsupported_op(lhs, op, rhs):
    expr = lhs + op + rhs if rhs else lhs + op
    with pytest.raises(NotImplementedException):
        interpret_token(expr, "expr")
