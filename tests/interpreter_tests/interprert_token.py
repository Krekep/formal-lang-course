from project.grammar.parser import parse
from project.grammar.interpreter.my_visitor import MyVisitor
from project.grammar.interpreter.my_types.AntlrType import AntlrType


def check_parser(text, token: str) -> bool:
    parser = parse(text)

    parser.removeErrorListeners()
    getattr(parser, token)()
    return parser.getNumberOfSyntaxErrors() == 0


def interpret_token(text: str, token: str) -> AntlrType:
    parser = parse(text)
    parser.removeErrorListeners()
    assert parser.getNumberOfSyntaxErrors() == 0

    tree = getattr(parser, token)()
    visitor = MyVisitor()
    value = visitor.visit(tree)
    return value
