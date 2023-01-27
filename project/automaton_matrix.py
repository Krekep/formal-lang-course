from scipy import sparse
from pyformlang.finite_automaton import (
    State,
    NondeterministicFiniteAutomaton,
    FiniteAutomaton,
    Symbol,
)

__all__ = ["AutomatonSetOfMatrix"]

from project.rsm import RSM


class AutomatonSetOfMatrix:
    """
    Class representing boolean matrix decomposition of finite automaton
    """

    def __init__(self):
        self.num_states = 0
        self.start_states = set()
        self.final_states = set()
        self.bool_matrices = {}
        self.state_indices = {}

    @classmethod
    def from_automaton(cls, automaton: FiniteAutomaton):
        """
        Transform automaton to set of labeled boolean matrix
        Parameters
        ----------
        automaton
            Automaton for transforming

        Returns
        -------
        AutomatonSetOfMatrix
            Result of transforming
        """

        automaton_matrix = cls()
        automaton_matrix.num_states = len(automaton.states)
        automaton_matrix.start_states = automaton.start_states
        automaton_matrix.final_states = automaton.final_states
        automaton_matrix.state_indices = {
            state: idx for idx, state in enumerate(automaton.states)
        }

        for s_from, trans in automaton.to_dict().items():
            for label, states_to in trans.items():
                if not isinstance(states_to, set):
                    states_to = {states_to}
                for s_to in states_to:
                    idx_from = automaton_matrix.state_indices[s_from]
                    idx_to = automaton_matrix.state_indices[s_to]
                    if label not in automaton_matrix.bool_matrices.keys():
                        automaton_matrix.bool_matrices[label] = sparse.csr_matrix(
                            (automaton_matrix.num_states, automaton_matrix.num_states),
                            dtype=bool,
                        )
                    automaton_matrix.bool_matrices[label][idx_from, idx_to] = True

        return automaton_matrix

    @classmethod
    def from_rsm(cls, rsm: RSM):
        """
        Transform automaton to set of labeled boolean matrix

        Parameters
        ----------
        rsm
            Automaton for transforming

        Returns
        -------
        AutomatonSetOfMatrix
            Result of transforming
        """

        states, start_states, final_states = set(), set(), set()
        for var, nfa in rsm.boxes.items():
            for s in nfa.states:
                state = State((var, s.value))
                states.add(state)
                if s in nfa.start_states:
                    start_states.add(state)
                if s in nfa.final_states:
                    final_states.add(state)

        states = sorted(states, key=lambda v: (v.value[0].value, v.value[1]))
        state_to_idx = {s: i for i, s in enumerate(states)}

        automaton_matrix = cls()
        automaton_matrix.num_states = len(states)
        automaton_matrix.start_states = start_states
        automaton_matrix.final_states = final_states
        automaton_matrix.state_indices = state_to_idx

        for var, nfa in rsm.boxes.items():
            for state_from, transitions in nfa.to_dict().items():
                for label, states_to in transitions.items():
                    if label not in automaton_matrix.bool_matrices.keys():
                        automaton_matrix.bool_matrices[label] = sparse.csr_matrix(
                            (automaton_matrix.num_states, automaton_matrix.num_states),
                            dtype=bool,
                        )
                    states_to = states_to if isinstance(states_to, set) else {states_to}
                    for state_to in states_to:
                        automaton_matrix.bool_matrices[label][
                            state_to_idx[State((var, state_from.value))],
                            state_to_idx[State((var, state_to.value))],
                        ] = True

        return automaton_matrix

    def to_automaton(self) -> NondeterministicFiniteAutomaton:
        """
        Transform set of labeled boolean matrix to automaton.

        Parameters
        ----------
        self
            Set of boolean matrix with label as key

        Returns
        -------
        AutomatonSetOfMatrix
            Resulting automaton
        """

        automaton = NondeterministicFiniteAutomaton()
        for label in self.bool_matrices.keys():
            for s_from, s_to in zip(*self.bool_matrices[label].nonzero()):
                automaton.add_transition(s_from, label, s_to)

        for state in self.start_states:
            automaton.add_start_state(State(state))

        for state in self.final_states:
            automaton.add_final_state(State(state))

        return automaton

    @property
    def get_states(self):
        return self.state_indices.keys()

    @property
    def get_start_states(self):
        return self.start_states.copy()

    @property
    def get_final_states(self):
        return self.final_states.copy()

    def get_nonterminals(self, s_from, s_to):
        return self.state_indices.get((s_from, s_to))

    def get_transitive_closure(self):
        """
        Get transitive closure of sparse.csr_matrix

        Parameters
        ----------
        self
            Class exemplar

        Returns
        -------
            Transitive closure
        """
        tc = sparse.csr_matrix((0, 0), dtype=bool)

        if len(self.bool_matrices) != 0:
            tc = sum(self.bool_matrices.values())
            prev_nnz = tc.nnz
            new_nnz = 0

            while prev_nnz != new_nnz:
                tc += tc @ tc
                prev_nnz, new_nnz = new_nnz, tc.nnz

        return tc

    def intersect(self, other):
        """
        Get intersection of two automatons
        Parameters
        ----------
        self
            First automaton
        other
            Second automaton

        Returns
        -------
        AutomatonSetOfMatrix
            Result of intersection
        """
        res = AutomatonSetOfMatrix()
        res.num_states = self.num_states * other.num_states
        common_labels = set(self.bool_matrices.keys()).union(other.bool_matrices.keys())

        for label in common_labels:
            if label not in self.bool_matrices.keys():
                self.bool_matrices[label] = sparse.csr_matrix(
                    (self.num_states, self.num_states), dtype=bool
                )
            if label not in other.bool_matrices.keys():
                other.bool_matrices[label] = sparse.csr_matrix(
                    (other.num_states, other.num_states), dtype=bool
                )

        for label in common_labels:
            res.bool_matrices[label] = sparse.kron(
                self.bool_matrices[label], other.bool_matrices[label], format="csr"
            )

        for state_first, state_first_idx in self.state_indices.items():
            for state_second, state_second_idx in other.state_indices.items():
                new_state = new_state_idx = (
                    state_first_idx * other.num_states + state_second_idx
                )
                res.state_indices[new_state] = new_state_idx

                if (
                    state_first in self.start_states
                    and state_second in other.start_states
                ):
                    res.start_states.add(new_state)

                if (
                    state_first in self.final_states
                    and state_second in other.final_states
                ):
                    res.final_states.add(new_state)
        return res
