from pyformlang.cfg import Variable
from pyformlang.finite_automaton import EpsilonNFA

from project.ecfg import ECFG


class RSM:
    """
    Recursive State Machine

    Attributes
    ----------
    start: Variable
        RSM start symbol
    boxes: dict[Variable, EpsilonNFA]
        RSM boxes
    """

    def __init__(self, start: Variable, boxes: dict[Variable, EpsilonNFA]):
        self.start = start
        self.boxes = boxes

    @classmethod
    def from_ecfg(cls, ecfg: ECFG) -> "RSM":
        """
        Create RSM for passed ECFG

        Parameters
        ----------
        ecfg: ECFG
            Grammar for transforming

        Returns
        -------
        rsm: RSM
            Result recursive stack machine
        """

        return cls(
            ecfg.start,
            {head: body.to_epsilon_nfa() for head, body in ecfg.productions.items()},
        )

    def minimize(self) -> "RSM":
        """
        Minimize RSM and return itself

        Returns
        -------
        rsm: RSM
            Minimized RSM
        """

        for var, nfa in self.boxes.items():
            self.boxes[var] = nfa.minimize()
        return self
