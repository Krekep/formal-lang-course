import project.manager
from project import manager
from project import parser

__all__ = ["run_console"]

_parser = parser.parser_initialize()


def run_console() -> None:
    """
    Runs a console application.

    Returns
    -------
    None
    """
    while True:
        stream = input(">>> ")
        try:
            args = _parser.parse_args(stream.split())
            args.func(args)
        except Exception as e:
            print(e)
