from project.grammar.interpreter.my_types.AntlrType import AntlrType

from project.grammar.interpreter.exceptions import NotImplementedException


class AntlrBool(AntlrType):
    """
    GQL boolean class

    Attributes
    ----------
    b: bool
        Internal boolean value
    """

    def __init__(self, b: bool):
        self.b = b

    def intersect(self, other: "AntlrBool") -> "AntlrBool":
        """
        'AND'
        Parameters
        ----------
        other: AntlrBool
            RHS boolean object
        Returns
        -------
        intersection: AntlrBool
            Logical 'AND'
        """
        return AntlrBool(self.b and other.b)

    def union(self, other: "AntlrBool") -> "AntlrBool":
        """
        'OR'
        Parameters
        ----------
        other: AntlrBool
            RHS boolean object
        Returns
        -------
        intersection: AntlrBool
            Logical 'OR'
        """
        return AntlrBool(self.b or other.b)

    def dot(self, other: "AntlrBool"):
        raise NotImplementedException("Bool doesn't support '.' operation")

    def kleene(self):
        raise NotImplementedException("Bool doesn't support '*' operation")

    def inverse(self) -> "AntlrBool":
        """
        'NOT'
        Returns
        -------
        complement: AntlrBool
            Logical 'NOT'
        """
        return AntlrBool(not self.b)

    def __bool__(self):
        return self.b

    def __eq__(self, other: "AntlrBool") -> bool:
        return self.b == other.b

    def __str__(self):
        return "true" if self.b else "false"

    def __hash__(self):
        return hash(self.b)
