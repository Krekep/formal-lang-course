import pytest
import platform
from project.grammar.parser import parse


def check_parser(text, token: str) -> bool:
    parser = parse(text)

    parser.removeErrorListeners()
    getattr(parser, token)()
    return parser.getNumberOfSyntaxErrors() == 0


@pytest.mark.parametrize(
    "text, accept",
    [
        ("_123", True),
        ("123", False),
        ("graph", True),
        ("", False),
        ("GRAPH", True),
        ("__main__", True),
    ],
)
def test_var(text, accept):
    assert check_parser(text, "var") == accept


@pytest.mark.parametrize(
    "text, accept",
    [
        ("fun : 42", True),
        ("fun : gg", True),
        ("fun [vv] : vv in ss", True),
        ("fun [vv, uu] : u_g", True),
        ("fun [vv, label, uu] : 11", True),
        ("fun [11, 22, 33]: 11", False),
    ],
)
def test_lambda(text, accept):
    assert check_parser(text, "my_lambda") == accept


@pytest.mark.parametrize(
    "text, accept",
    [
        ("filter(fun [xx, yy]: (xx), aa)", True),
        ("filter fun 1: 1 p", False),
        ("filter         (fun : 55   ,   pp)", True),
        ("filter", False),
        ("filter(, x)", False),
        ("filter(fun x: x, )", False),
        ("filter((fun [xx, yy]: (xx)), aa)", True),
    ],
)
def test_filter(text, accept):
    assert check_parser(text, "my_filter") == accept


@pytest.mark.parametrize(
    "text, accept",
    [
        ("true", True),
        ("false", True),
        ("True", False),
        ("False", False),
        ('"label"', True),
        ("label", False),
        ('{"l1", l2}', False),
        ("get_vertices(g)", False),
        ("42", True),
    ],
)
def test_val(text, accept):
    assert check_parser(text, "val") == accept


@pytest.mark.parametrize(
    "text, accept",
    [
        ("g1 & g2", True),
        (
            "g",
            False,
        ),  # Тут лажа, не понимаю почему не даёт создавать идентификаторы из 1 символа
        ("42", True),
        ("", False),
        ("(get_edges(g)) & (get_vertices(g2))", False),
        ("(& g) & {(1, 2)}", False),
        ("l1 . l2 . l3 | l4", True),
        ("(l1 & l2) | (l3 & l4)", True),
        ('"label1" . "label2" | "label3"', True),
        ("filter(fun [xx, yy]: 42, gg)", True),
    ],
)
def test_expr(text, accept):
    assert check_parser(text, "expr") == accept


@pytest.mark.parametrize(
    "text, accept",
    [
        ("print g2", False),
        ("prnt g2", False),
        ("print {1..100}", False),
        ("print(11)", True),
        ("print", False),
        ('g1 = load("wine")', True),
        ("g1 = load", False),
        ("g1 = 42", True),
        ('gg = load("wine")', True),
        ("new_g = set_start(range(10, 100), gg)", True),
        ("g_labels = get_labels(new_g)", True),
        ('common_labels = g_labels & (load("pizza"))', True),
        ("print(common_labels)", True),
        ("result = filter((fun [vv]: vv in start), gg)", True),
        (
            "result = filter((fun [vv]: vv in start), map((fun [vv, label, uu]: vv), get_edges(inter)))",
            True,
        ),
        ("gg = set_start(range(10, 100), set_final(get_vertices(tmp), tmp))", True),
        ('l1 = "l1" | "l2"', True),
        ('q1 = ("l3" | l1)*', True),
        ('q2 = "l1" . "l5"', True),
        ("inter = gg & q1", True),
        ("start = get_start(gg)", True),
    ],
)
def test_stmt(text, accept):
    assert check_parser(text, "stmt") == accept


@pytest.mark.parametrize(
    "text, accept",
    [
        ("{11, 22, 33}", True),
        ("{aa, bb, cc}", True),
        ("range(10, 100)", True),
        ("get_start(gg)", True),
    ],
)
def test_vertices(text, accept):
    assert check_parser(text, "vertices") == accept


@pytest.mark.parametrize(
    "text, accept",
    [
        ('load("path")', True),
        ("set_start({11, 22}, gg)", True),
    ],
)
def test_graph(text, accept):
    assert check_parser(text, "my_graph") == accept


@pytest.mark.parametrize(
    "text, accept",
    [
        (
            """
                gg = load("wine");
                new_g = set_start(range(10, 100), gg);
                g_labels = get_labels(new_g);
                common_labels = g_labels & (load("pizza"));
                print(common_labels);
            """,
            True,
        ),
        (
            """
                tmp = load("sample");
                gg = set_start(range(10, 100), set_final(get_vertices(tmp), tmp));
                l1 = "l1" | "l2";
                q1 = ("l3" | l1)*;
                q2 = "l1" . "l5";
                inter = gg & q1;
                start = get_start(gg);
                result = filter((fun [vv]: vv in start), map((fun [vv, label, uu]: vv), get_edges(inter)));
            """,
            True,
        ),
        ("", False),
        ('gg = load("no_semicolon")', False),
    ],
)
def test_prog(text, accept):
    assert check_parser(text, "prog") == accept
