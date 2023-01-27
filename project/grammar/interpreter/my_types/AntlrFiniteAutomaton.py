from project.grammar.interpreter.my_types.AntlrAutomata import AntlrAutomata
from project.grammar.interpreter.my_types.AntlrCFG import AntlrCFG
from project.grammar.interpreter.my_types.AntlrSet import AntlrSet
from project.fa_utils import regex_to_dfa, replace_nfa_states, add_nfa_states
from project.graph_utils import graph_to_nfa
from project.automaton_matrix import AutomatonSetOfMatrix
from project.rpq import get_reachable


from networkx import MultiDiGraph
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton

from project.grammar.interpreter.exceptions import (
    NotImplementedException,
    ConversionException,
    AntlrTypeError,
)


class AntlrFiniteAutomaton(AntlrAutomata):
    """
    Representation of Finite-Automata

    Attributes
    ----------
    nfa: NondeterministicFiniteAutomaton
        Internal nfa object
    """

    def __init__(self, nfa: NondeterministicFiniteAutomaton):
        self.nfa = nfa

    @classmethod
    def from_graph(cls, graph: MultiDiGraph) -> "AntlrFiniteAutomaton":
        """

        Parameters
        ----------
        graph: MultiDiGraph
            Transform graph into automata

        Returns
        -------
        fa: AntlrFiniteAutomaton
            Automata transformed from graph
        """
        return cls(nfa=graph_to_nfa(graph))

    @classmethod
    def from_string(cls, regex_str: str) -> "AntlrFiniteAutomaton":
        """

        Parameters
        ----------
        regex_str: str
            Transform regular-expression string into automata

        Returns
        -------
        fa: AntlrFiniteAutomaton
            Automata transformed from string

        Raises
        ------
        ConversionException
            If given string violates regular expression rules
        """
        try:
            return AntlrFiniteAutomaton(nfa=regex_to_dfa(regex_str))
        except Exception as exc:
            raise ConversionException("Regular string", "str") from exc

    def __intersect_fa(self, other: "AntlrFiniteAutomaton") -> "AntlrFiniteAutomaton":
        """
        Inner intersection (FA & FA) function

        Parameters
        ----------
        other: AntlrFiniteAutomaton
            Finite Automata

        Returns
        -------
        intersection: AntlrFiniteAutomaton
            Intersection of two FA
        """
        lhs = AutomatonSetOfMatrix.from_automaton(self.nfa)
        rhs = AutomatonSetOfMatrix.from_automaton(other.nfa)
        intersection = lhs.intersect(rhs)
        intersection_automaton = intersection.to_automaton()
        return AntlrFiniteAutomaton(nfa=intersection_automaton)

    def __intersect_cfg(self, other: AntlrCFG) -> AntlrCFG:
        """
        Inner intersection (FA & CFG) function

        Parameters
        ----------
        other: AntlrCFG
            Context Free Grammar
        Returns
        -------
        intersection: AntlrCFG
            Intersection of FA with GQLCFG
        """
        intersection = other.intersect(self)
        return intersection

    def intersect(self, other: AntlrAutomata) -> AntlrAutomata:
        """
        Automata & Automata intersection

        Parameters
        ----------
        other: AntlrCFG | AntlrFiniteAutomaton
            CFG or FA object

        Returns
        -------
        intersection: AntlrAutomata
            cfg, IF 'other' is GQLCFG
            fa, IF 'other' is AntlrFiniteAutomaton

        Raises
        ------
        AntlrTypeError
            If object does not represent FA or CFG
        """
        if isinstance(other, AntlrFiniteAutomaton):
            return self.__intersect_fa(other=other)
        if isinstance(other, AntlrCFG):
            return self.__intersect_cfg(other=other)

        raise AntlrTypeError(f"Expected AntlrAutomata, got {str(type(other))} instead")

    def union(self, other: "AntlrFiniteAutomaton") -> "AntlrFiniteAutomaton":
        """

        Parameters
        ----------
        other: AntlrFiniteAutomaton
            rhs FA

        Returns
        -------
        union: AntlrFiniteAutomaton
            Union of two FA
        """
        return AntlrFiniteAutomaton(self.nfa.union(other.nfa).to_deterministic())

    def dot(self, other: "AntlrFiniteAutomaton") -> "AntlrFiniteAutomaton":
        """

        Parameters
        ----------
        other: AntlrFiniteAutomaton
            rhs FA

        Returns
        -------
        dot: AntlrFiniteAutomaton
            Dot of two FA
        """
        lhs = self.nfa.to_regex()
        rhs = other.nfa.to_regex()
        return AntlrFiniteAutomaton(
            lhs.concatenate(rhs).to_epsilon_nfa().to_deterministic()
        )

    def inverse(self) -> "AntlrFiniteAutomaton":
        """
        Get complement of FA

        Returns
        -------
        complement: AntlrFiniteAutomaton
            Complement of FA
        """
        return AntlrFiniteAutomaton(self.nfa.get_complement().to_deterministic())

    def kleene(self) -> "AntlrFiniteAutomaton":
        """

        Returns
        -------
        kleene: AntlrFiniteAutomaton
            Kleene closure of FA
        """
        return AntlrFiniteAutomaton(nfa=self.nfa.kleene_star().to_deterministic())

    def __str__(self):
        return str(self.nfa.minimize().to_regex())

    def set_start(self, start_states: AntlrSet) -> "AntlrFiniteAutomaton":
        nfa = replace_nfa_states(self.nfa, start_states=start_states.data)
        return AntlrFiniteAutomaton(nfa)

    def set_final(self, final_states: AntlrSet) -> "AntlrFiniteAutomaton":
        nfa = replace_nfa_states(self.nfa, final_states=final_states.data)
        return AntlrFiniteAutomaton(nfa)

    def add_start(self, start_states: AntlrSet) -> "AntlrFiniteAutomaton":
        nfa = add_nfa_states(self.nfa, start_states=start_states.data)
        return AntlrFiniteAutomaton(nfa)

    def add_final(self, final_states: AntlrSet) -> "AntlrFiniteAutomaton":
        nfa = add_nfa_states(self.nfa, final_states=final_states.data)
        return AntlrFiniteAutomaton(nfa)

    @staticmethod
    def __get_reachable(nfa: NondeterministicFiniteAutomaton) -> set:
        """
        Internal helper function to get reachable vertices set

        Parameters
        ----------
        nfa: NondeterministicFiniteAutomaton
            Finite Automata
        Returns
        -------
        reachable: set
            Reachable vertices set
        """
        graph_bm = AutomatonSetOfMatrix.from_automaton(nfa)
        query_bm = AutomatonSetOfMatrix.from_automaton(regex_to_dfa("epsilon"))
        return get_reachable(graph_bm, query_bm)

    def get_reachable(self) -> AntlrSet:
        """

        Returns
        -------
        reachable: AntlrSet
            Reachable vertices set
        """
        return AntlrSet(AntlrFiniteAutomaton.__get_reachable(self.nfa))

    @property
    def start(self) -> AntlrSet:
        return AntlrSet(self.nfa.start_states)

    @property
    def final(self) -> AntlrSet:
        return AntlrSet(self.nfa.final_states)

    @property
    def labels(self) -> AntlrSet:
        return AntlrSet(self.nfa.symbols)

    @property
    def edges(self) -> AntlrSet:
        raise NotImplementedException("AntlrFiniteAutomaton.edges")

    @property
    def vertices(self) -> AntlrSet:
        return AntlrSet(self.nfa.states)
