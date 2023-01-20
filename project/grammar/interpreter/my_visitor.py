from project.grammar.antlr_grammarVisitor import antlr_grammarVisitor
from project.grammar.antlr_grammarParser import antlr_grammarParser
from project.grammar.interpreter.my_types.AntlrBool import AntlrBool

from project.grammar.interpreter.my_types.AntlrType import AntlrType
from project.grammar.interpreter.my_types.AntlrAutomata import AntlrAutomata
from project.grammar.interpreter.my_types.AntlrFiniteAutomaton import AntlrFiniteAutomaton
from project.grammar.interpreter.my_types.AntlrSet import AntlrSet

from project.grammar.interpreter.memory import Memory

from project.manager import get_graph
from project.grammar.interpreter.exceptions import GQLTypeError

from antlr4 import ParserRuleContext
from typing import Union
from collections import namedtuple

import sys


Fun = namedtuple("Fun", ["params", "body"])


class MyVisitor(antlr_grammarVisitor):
    def __init__(self):
        self.memory = Memory()

    def visitProg(self, ctx: ParserRuleContext):
        return self.visitChildren(ctx)

    def visitExpr(self, ctx: antlr_grammarParser.ExprContext) -> AntlrType:
        binary_op = {"AND": "intersect", "OR": "union", "DOT": "dot", "IN": "find"}
        unary_op = {"NOT": "inverse", "KLEENE": "kleene"}
        for b_op in binary_op:
            if getattr(ctx, b_op)():
                lhs = self.visit(ctx.expr(0))
                rhs = self.visit(ctx.expr(1))
                if b_op == "IN":
                    lhs, rhs = rhs, lhs
                return getattr(lhs, binary_op[b_op])(rhs)
        for u_op in unary_op:
            if getattr(ctx, u_op)():
                lhs = self.visit(ctx.expr(0))
                return getattr(lhs, unary_op[u_op])()

        return self.visitChildren(ctx)

    def visitStmt(self, ctx: antlr_grammarParser.StmtContext):
        if ctx.var():
            name = ctx.var().getText()
            value = self.visit(ctx.expr())
            self.memory.add(name, value)

        else:
            value = self.visit(ctx.expr())
            sys.stdout.write(str(value) + "\n")

    def visitString(self, ctx: antlr_grammarParser.StringContext):
        value = ctx.STRING().getText()
        return value

    def visitBool(self, ctx: antlr_grammarParser.BoolContext):
        return AntlrBool(ctx.TRUE() is not None)

    def visitInt(self, ctx: antlr_grammarParser.IntContext):
        return int(ctx.INT().getText())

    def visitVar(self, ctx: antlr_grammarParser.VarContext, is_search: bool = True):
        name = ctx.IDENTIFIER().getText()
        if is_search:
            return self.memory.find(name)
        return name

    def visitVertex(self, ctx: antlr_grammarParser.VertexContext):
        if ctx.var():
            name = ctx.var().getText()
            return self.memory.find(name)
        else:
            return int(ctx.INT().getText())

    def visitMy_range(self, ctx: antlr_grammarParser.My_rangeContext):
        start = int(ctx.INT(0).getText())
        end = int(ctx.INT(1).getText())
        return AntlrSet(set(range(start, end + 1)))

    def visitVertices_set(self, ctx: antlr_grammarParser.Vertices_setContext):
        vertices_set = set()
        for vertex in ctx.vertex():
            vertices_set.add(self.visitVertex(vertex))

        return AntlrSet(vertices_set)

    def visitLabel(self, ctx: antlr_grammarParser.LabelContext):
        lab_str = self.visit(ctx.string())
        return AntlrFiniteAutomaton.from_string(lab_str)

    def visitLabels_set(self, ctx: antlr_grammarParser.Labels_setContext):
        labels_set = set()
        for label in ctx.label():
            labels_set.add(self.visitLabel(label))

        return AntlrSet(labels_set)

    def visitEdge(self, ctx: antlr_grammarParser.EdgeContext):
        vertex_from = self.visit(ctx.vertex(0))
        label = self.visit(ctx.label())
        vertex_to = self.visit(ctx.vertex(1))
        return vertex_from, label, vertex_to

    def visitEdges(self, ctx: antlr_grammarParser.EdgesContext):
        return self.visitChildren(ctx)

    def visitEdges_set(self, ctx: antlr_grammarParser.Edges_setContext):
        edges_set = set()
        for edge in ctx.edge():
            edges_set.add(self.visitEdge(edge))

        return AntlrSet(edges_set)

    def visitMy_lambda(self, ctx: antlr_grammarParser.My_lambdaContext) -> Fun:
        lambda_context = {}
        for v in ctx.var():
            lambda_context[self.visitVar(v, is_search=False)] = None

        params = lambda_context
        body = ctx.expr()

        return Fun(params=params, body=body)

    def _apply_lambda(self, fun: Fun, value: AntlrType) -> AntlrType:
        key = next(iter(fun.params))
        self.memory = self.memory.next_scope()
        self.memory.add(key, value)
        result = self.visit(fun.body)
        self.memory = self.memory.remove_last()
        return result

    def _iter_method(
        self,
        ctx: Union[antlr_grammarParser.My_mapContext, antlr_grammarParser.My_filterContext],
        method="map",
    ):
        fun = self.visit(ctx.my_lambda())
        iterable = self.visit(ctx.expr())
        if not isinstance(iterable, AntlrSet):
            raise GQLTypeError(
                msg=f"Can not apply map on {type(iterable)} object. Set expected."
            )
        if len(iterable) == 0:
            return iterable
        first_elem = next(iter(iterable.data))
        param_count = len(first_elem.data) if isinstance(first_elem, AntlrSet) else 1
        if len(fun.params) != param_count:
            raise GQLTypeError(
                msg=f"Lambda argument count mismatched: Expected {len(fun.params)} Got {param_count}"
            )
        new_iterable = set()
        for elem in iterable.data:
            result = self._apply_lambda(fun, elem)
            if method == "map":
                new_iterable.add(result)
            elif method == "filter":
                if result:
                    new_iterable.add(elem)
            else:
                raise NotImplementedError(
                    f"MyVisitor._iter_method wrong method {method}"
                )

        return AntlrSet(internal_set=new_iterable)

    def visitMy_map(self, ctx: antlr_grammarParser.My_mapContext):
        return self._iter_method(ctx, method="map")

    def visitMy_filter(self, ctx: antlr_grammarParser.My_filterContext):
        return self._iter_method(ctx, method="filter")

    def visitMy_graph(self, ctx: antlr_grammarParser.My_graphContext) -> AntlrAutomata:
        return self.visitChildren(ctx)

    def visitLoad_graph(self, ctx: antlr_grammarParser.Load_graphContext):
        name = self.visit(ctx.string()).strip('"')
        return _get_graph_by_name(name)

    def _modify_states(
        self,
        ctx: Union[
            antlr_grammarParser.Set_startContext,
            antlr_grammarParser.Add_startContext,
            antlr_grammarParser.Set_finalContext,
            antlr_grammarParser.Add_finalContext,
        ],
        modify_method=None,
    ):
        graph = self.visit(ctx.my_graph())
        vertices = self.visit(ctx.vertices())

        return getattr(graph, modify_method)(vertices)

    def visitSet_final(self, ctx: antlr_grammarParser.Set_finalContext):
        return self._modify_states(ctx, modify_method="set_final")

    def visitSet_start(self, ctx: antlr_grammarParser.Set_startContext):
        return self._modify_states(ctx, modify_method="set_start")

    def visitAdd_start(self, ctx: antlr_grammarParser.Add_startContext):
        return self._modify_states(ctx, modify_method="add_start")

    def visitAdd_final(self, ctx: antlr_grammarParser.Add_finalContext):
        return self._modify_states(ctx, modify_method="add_final")

    def _get_graph_info(
        self,
        ctx: Union[
            antlr_grammarParser.Get_edgesContext,
            antlr_grammarParser.Get_labelsContext,
            antlr_grammarParser.Get_startContext,
            antlr_grammarParser.Get_finalContext,
            antlr_grammarParser.Get_verticesContext,
            antlr_grammarParser.Get_reachableContext,
        ],
        info_method=None,
    ):
        graph = self.visit(ctx.my_graph())
        return getattr(graph, info_method)

    def visitGet_edges(self, ctx: antlr_grammarParser.Get_edgesContext):
        return self._get_graph_info(ctx, info_method="edges")

    def visitGet_labels(self, ctx: antlr_grammarParser.Get_labelsContext):
        return self._get_graph_info(ctx, info_method="labels")

    def visitGet_start(self, ctx: antlr_grammarParser.Get_startContext):
        return self._get_graph_info(ctx, info_method="start")

    def visitGet_final(self, ctx: antlr_grammarParser.Get_finalContext):
        return self._get_graph_info(ctx, info_method="final")

    def visitGet_vertices(self, ctx: antlr_grammarParser.Get_verticesContext):
        return self._get_graph_info(ctx, info_method="vertices")

    def visitGet_reachable(self, ctx: antlr_grammarParser.Get_reachableContext):
        graph = self.visit(ctx.my_graph())
        return graph.get_reachable()


def _get_graph_by_name(name: str) -> "AntlrFiniteAutomaton":
    try:
        graph = get_graph(graph_name=name)
    except Exception as e:
        raise e

    return AntlrFiniteAutomaton.from_graph(graph)
