from interprert_token import interpret_token
from project.grammar.interpreter.my_types.AntlrSet import AntlrSet
from project.grammar.interpreter.exceptions import (
    NotImplementedException,
    AntlrTypeError,
)

import pytest


@pytest.mark.parametrize(
    "lhs, op, rhs, expected",
    [
        ("{11, 22, 33, 44, 55}", "&", "{22, 33, 44}", {22, 33, 44}),
        ("{11, 22, 33}", "|", "{44, 55, 66}", {11, 22, 33, 44, 55, 66}),
        ("{11, 22, 33}", "&", "{}", set()),
        ("{}", "|", "{}", set()),
    ],
)
def test_binary(lhs, op, rhs, expected):
    expression = lhs + op + rhs
    actual_set = interpret_token(expression, "expr")
    expected_set = AntlrSet(expected)
    assert actual_set.data == expected_set.data


@pytest.mark.parametrize(
    "lhs, op, rhs",
    [
        ("{11, 22}", ".", "{11, 22, 33}"),
        ("{11, 22, 33}", "*", ""),
        ("", "not", "{11, 22, 33}"),
    ],
)
def test_unsupported_op(lhs, op, rhs):
    expression = lhs + op + rhs
    with pytest.raises(NotImplementedException):
        interpret_token(expression, "expr")


@pytest.mark.parametrize(
    "range_expr, expected",
    [
        ("{10..15}", {10, 11, 12, 13, 14, 15}),
        ("{11..11}", {11}),
    ],
)
def test_range(range_expr, expected):
    actual_set = interpret_token(range_expr, "my_range")
    assert actual_set.data == AntlrSet(expected).data


def test_mismatched_types():
    lhs = "{11, 22, 33}"
    rhs = '{"11", "22", "33"}'
    expr = lhs + "&" + rhs
    with pytest.raises(AntlrTypeError):
        interpret_token(expr, "expr")
