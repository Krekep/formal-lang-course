from antlr4 import InputStream, CommonTokenStream

from project.grammar.antlr_grammarLexer import antlr_grammarLexer
from project.grammar.antlr_grammarParser import antlr_grammarParser
from project.grammar.antlr_grammarListener import antlr_grammarListener

from antlr4 import ParseTreeWalker, ParserRuleContext
from antlr4.error.Errors import ParseCancellationException
from antlr4.tree.Tree import TerminalNodeImpl
from pydot import Dot, Edge, Node

__all__ = ["parse", "check_parser_correct"]


def parse(text: str) -> antlr_grammarParser:
    input_stream = InputStream(text)
    lexer = antlr_grammarLexer(input_stream)
    lexer.removeErrorListeners()
    stream = CommonTokenStream(lexer)
    parser = antlr_grammarParser(stream)

    return parser


def check_parser_correct(text: str) -> bool:
    parser = parse(text)
    parser.removeErrorListeners()
    _ = parser.prog()
    return parser.getNumberOfSyntaxErrors() == 0


def generate_dot(text: str, path: str):
    if not check_parser_correct(text):
        raise ParseCancellationException("The word doesn't match the grammar")
    ast = parse(text).prog()
    tree = Dot("tree", graph_type="digraph")
    ParseTreeWalker().walk(DotTreeListener(tree, antlr_grammarParser.ruleNames), ast)
    tree.write(path)
    return path


class DotTreeListener(antlr_grammarListener):
    def __init__(self, tree: Dot, rules):
        self.tree = tree
        self.num_nodes = 0
        self.nodes = {}
        self.rules = rules
        super(DotTreeListener, self).__init__()

    def enterEveryRule(self, ctx: ParserRuleContext):
        if ctx not in self.nodes:
            self.num_nodes += 1
            self.nodes[ctx] = self.num_nodes
        if ctx.parentCtx:
            self.tree.add_edge(Edge(self.nodes[ctx.parentCtx], self.nodes[ctx]))
        label = self.rules[ctx.getRuleIndex()]
        self.tree.add_node(Node(self.nodes[ctx], label=label))

    def visitTerminal(self, node: TerminalNodeImpl):
        self.num_nodes += 1
        self.tree.add_edge(Edge(self.nodes[node.parentCtx], self.num_nodes))
        self.tree.add_node(Node(self.num_nodes, label=f"TERM: {node.getText()}"))
