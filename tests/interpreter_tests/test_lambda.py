from interprert_token import interpret_token
from project.grammar.interpreter.my_types.AntlrBool import AntlrBool

import pytest


@pytest.mark.parametrize(
    "initial_set, fun, expected_set",
    [
        ("{11, 22}", "fun [xx] : xx in {22}", {AntlrBool(True), AntlrBool(False)}),
        ("{11, 22, 33}", "fun [xx] : 55", {55}),
    ],
)
def test_map(initial_set, fun, expected_set):
    expr = f"map({fun}, {initial_set})"
    actual = interpret_token(expr, "my_map")
    assert actual.data == expected_set


@pytest.mark.parametrize(
    "initial_set, fun, expected_set",
    [
        ("{11, 22, 33, 44, 55}", "fun [xx]: xx in range(22, 44)", "{22, 33, 44}"),
    ],
)
def test_filter(initial_set, fun, expected_set):
    expr = f"filter({fun}, {initial_set})"
    actual = interpret_token(expr, "my_filter")
    expected = interpret_token(expected_set, "vertices")
    assert actual.data == expected.data
