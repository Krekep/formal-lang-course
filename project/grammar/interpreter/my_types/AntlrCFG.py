from project.grammar.interpreter.my_types.AntlrAutomata import AntlrAutomata
from project.grammar.interpreter.my_types.AntlrSet import AntlrSet

from pyformlang.cfg import CFG
from project.ecfg import ECFG
from project.rsm import RSM
from project.automaton_matrix import AutomatonSetOfMatrix

from project.grammar.interpreter.exceptions import (
    NotImplementedException,
    ConversionException,
    GQLTypeError,
)


class AntlrCFG(AntlrAutomata):
    """
    Representation of Context-Free-Grammar

    Attributes
    ----------
    cfg: CFG
        Internal CFG object
    """

    def __init__(self, cfg: CFG):
        self.cfg = cfg

    @classmethod
    def from_text(cls, text: str):
        """

        Parameters
        ----------
        text: str
            String given in terms of CFG
            E.g. 'S -> a S
                  S -> epsilon'
        Returns
        -------
        cfg: AntlrCFG
            Object transformed from text

        Raises
        ------
        ConversionException
            If text violates CFG format
        """
        try:
            cfg = CFG.from_text(text=text)
            return cls(cfg=cfg)
        except ValueError as e:
            raise ConversionException("str", "CFG") from e

    def intersect(self, other: AntlrAutomata) -> "AntlrCFG":
        """

        Parameters
        ----------
        other: AntlrFiniteAutomaton
            Finite automata (regular expression)

        Returns
        -------
        intersection: AntlrCFG
            Intersection of CFG and FA

        Raises
        ------
        GQLTypeError
            If 'other' type is not AntlrFiniteAutomaton
        """
        if not isinstance(other, AntlrAutomata):
            raise GQLTypeError(
                f"Expected finite automata, got {str(type(other))} instead"
            )

        if isinstance(other, AntlrCFG):
            raise GQLTypeError(f"Can't intersect CFG with another CFG")

        intersection = self.cfg.intersection(other.nfa)

        return AntlrCFG(cfg=intersection)

    def union(self, other: AntlrAutomata) -> "AntlrCFG":
        """

        Parameters
        ----------
        other: AntlrAutomata
            Automata object

        Returns
        -------
        union: AntlrCFG
            Union of CFG with 'other'
        """
        if isinstance(other, AntlrCFG):
            return AntlrCFG(cfg=self.cfg.union(other.cfg))

        raise NotImplementedException("Union is implemented only for AntlrCFG types")

    def dot(self, other: AntlrAutomata) -> "AntlrCFG":
        """
        Concatenation of CFG with another automata

        Parameters
        ----------
        other: AntlrAutomata
            Automata object
        Returns
        -------
        concatenation: AntlrCFG
            Concatenation of CFG and 'other'
        """
        if isinstance(other, AntlrCFG):
            return AntlrCFG(cfg=self.cfg.concatenate(other.cfg))

        raise NotImplementedException("Dot is implemented only for AntlrCFG types")

    def inverse(self):
        raise NotImplementedException("AntlrCFG.inverse")

    def kleene(self):
        raise NotImplementedException("AntlrCFG.kleene")

    def __str__(self):
        return self.cfg.to_text()

    def setStart(self, start_states):
        raise NotImplementedException("Can't set start symbol to CFG after creation")

    def setFinal(self, final_states):
        raise NotImplementedException("Can't set final symbol to CFG")

    def addStart(self, start_states):
        raise NotImplementedException("Can't add more start symbols to CFG")

    def addFinal(self, final_states):
        raise NotImplementedException("Can't add final symbols to CFG")

    @property
    def start(self) -> AntlrSet:
        return AntlrSet(self.cfg.start_symbol.value)

    @property
    def final(self) -> AntlrSet:
        return AntlrSet(set(self.cfg.get_reachable_symbols()))

    @property
    def labels(self) -> AntlrSet:
        return AntlrSet(set(self.cfg.terminals))

    @property
    def edges(self) -> AntlrSet:
        raise NotImplementedException("AntlrCFG.edges")

    @property
    def vertices(self) -> AntlrSet:
        return AntlrSet(set(self.cfg.variables))

    def get_reachable(self) -> AntlrSet:
        """
        Get reachable vertices from the start

        Returns
        -------
        reachable: AntlrSet
            Set of reachable vertices
        """
        ecfg = ECFG.from_pyformlang_cfg(self.cfg)
        rsm = RSM.from_ecfg(ecfg)
        rsm_bm = AutomatonSetOfMatrix.from_rsm(rsm)
        tc = rsm_bm.get_transitive_closure()
        reachable = set()
        for i, j in zip(*tc.nonzero()):
            reachable.add((i, rsm_bm.get_nonterminals(i, j), j))

        return AntlrSet(reachable)
