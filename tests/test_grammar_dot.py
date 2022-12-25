import sys

import pytest

from pathlib import Path


# if sys.platform.startswith("win"):
#     pytest.skip("skipping", allow_module_level=True)
# else:
#     from project.grammar.parser import generate_dot
from project.grammar.parser import generate_dot
from antlr4.error.Errors import ParseCancellationException


def test_write_dot():
    text = """
    gg = load("bzip");
    g1 = set_final(get_vertices(gg), set_start(range(11, 100), gg));

    qq = ("l" . "r"*)*;
    res = g1 & qq;
    print(res);
    """
    path = generate_dot(text, "data/test_grammar.dot")
    assert path == "data/test_grammar.dot"


def test_incorrect_text():
    text = """
    g = load("bzip");
    g1 = set_final(get_vertices(g), set_start(range(1, 100), g));

    q = ("l" . "r"*)*
    res = g1 & q;
    print res
    """
    with pytest.raises(ParseCancellationException):
        generate_dot(text, "test")
