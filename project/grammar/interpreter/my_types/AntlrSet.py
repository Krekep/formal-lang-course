from project.grammar.interpreter.my_types.AntlrType import AntlrType
from project.grammar.interpreter.my_types.AntlrBool import AntlrBool

from project.grammar.interpreter.exceptions import GQLTypeError, NotImplementedException


class AntlrSet(AntlrType):
    """
    Set object with additional type checking

    Attributes
    ----------
    internal_set: set
        Python set object
    """

    def __init__(self, internal_set: set):
        self._internal_type = AntlrSet.get_type(internal_set)
        self._internal_set = internal_set

    @staticmethod
    def get_type(set_obj: set) -> type:
        """

        Parameters
        ----------
        set_obj: set
            Python set object

        Returns
        -------
        t: type
            First element type
        """
        if len(set_obj) == 0:
            return type(None)
        iseq = iter(set_obj)
        return type(next(iseq))

    @staticmethod
    def _type_consistency(set_obj: set) -> bool:
        """

        Parameters
        ----------
        set_obj: set
            Python set object

        Returns
        -------
        is_consistent: bool
            True if elements have one type, False otherwise
        """
        if len(set_obj) == 0:
            return True
        iseq = iter(set_obj)
        t = type(next(iseq))
        return all(map(lambda x: isinstance(x, t), iseq))

    @classmethod
    def fromSet(cls, pyset: set) -> "AntlrSet":
        """

        Parameters
        ----------
        pyset: set
            Python set object
        Returns
        -------
        set: AntlrSet
            GQLSet object

        Raises
        ------
        GQLTypeError
            If set type is inconsistent
        """
        if not AntlrSet._type_consistency(pyset):
            raise GQLTypeError("Set type is inconsistent!")
        return AntlrSet(pyset)

    @property
    def t(self) -> type:
        return self._internal_type

    @property
    def data(self) -> set:
        return self._internal_set

    def __len__(self):
        return len(self._internal_set)

    def find(self, value) -> AntlrBool:
        """
        Check whether value in set or not

        Parameters
        ----------
        value
            searchable object
        Returns
        -------
        b: AntlrBool
            True if value is in internal set, False otherwise
        """
        return AntlrBool(value in self._internal_set)

    def intersect(self, other: "AntlrSet") -> "AntlrSet":
        """
        Two sets intersection

        Parameters
        ----------
        other: AntlrSet
            Another set object to intersect

        Returns
        -------
        intersection: AntlrSet
            Intersection of two sets

        Raises
        ------
        GQLTypeError
            If given sets have different types
        """
        if self.data and other.data and self.t != other.t:
            raise GQLTypeError(f"Types mismatched: {self.t} != {other.t}")
        return AntlrSet(internal_set=self.data & other.data)

    def union(self, other: "AntlrSet") -> "AntlrSet":
        """
        Two sets union

        Parameters
        ----------
        other: AntlrSet
            Another set object to unite

        Returns
        -------
        union: AntlrSet
            Union of two sets

        Raises
        ------
        GQLTypeError
            If given sets have different types
        """
        if self.data and other.data and self.t != other.t:
            raise GQLTypeError(f"Types mismatched: {self.t} != {other.t}")
        return AntlrSet(internal_set=self.data | other.data)

    def dot(self, other):
        raise NotImplementedException("Set dot")

    def kleene(self):
        raise NotImplementedException("Set kleene")

    def inverse(self):
        raise NotImplementedException("Set inverse")

    def __str__(self):
        return "{" + ", ".join(map(lambda x: str(x), self.data)) + "}"
