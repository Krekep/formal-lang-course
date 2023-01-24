from project.grammar.interpreter.intepreter import read_script, interpreter
from project.grammar.interpreter.exceptions import (
    ScriptPathException,
    ScriptExtensionException,
)

from pathlib import Path

import pytest


def test_invalid_file_path():
    with pytest.raises(ScriptPathException):
        read_script(filename=Path("sometext").absolute())


def test_invalid_extension():
    with pytest.raises(ScriptExtensionException):
        read_script(
            filename=Path("tests/interpreter_tests/data/invalid_extension.mgql")
        )


@pytest.mark.parametrize(
    "script_path",
    [
        "tests/interpreter_tests/data/common_labels.gql",
        "tests/interpreter_tests/data/common_labels_filter.gql",
        "tests/interpreter_tests/data/regex_intersection.gql",
        "tests/interpreter_tests/data/rpq.gql",
        "tests/interpreter_tests/data/print_test.gql",
    ],
)
def test_correct_script(script_path):
    assert interpreter([Path(script_path)]) == 0
