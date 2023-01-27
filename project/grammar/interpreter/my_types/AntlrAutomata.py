from abc import ABC, abstractmethod

from project.grammar.interpreter.my_types.AntlrType import AntlrType


class AntlrAutomata(AntlrType, ABC):
    """
    Base class for Automata (GQLRSM, AntlrFiniteAutomaton)
    """

    @abstractmethod
    def set_start(self, start_states):
        pass

    @abstractmethod
    def set_final(self, final_states):
        pass

    @abstractmethod
    def add_start(self, start_states):
        pass

    @abstractmethod
    def add_final(self, final_states):
        pass

    @abstractmethod
    def get_reachable(self):
        pass

    @property
    @abstractmethod
    def start(self):
        pass

    @property
    @abstractmethod
    def final(self):
        pass

    @property
    @abstractmethod
    def labels(self):
        pass

    @property
    @abstractmethod
    def edges(self):
        pass

    @property
    @abstractmethod
    def vertices(self):
        pass
