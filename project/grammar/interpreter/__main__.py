import sys

from project.grammar.interpreter import intepreter
from project.grammar.interpreter.exceptions import RunTimeException


def main(*argv):
    try:
        intepreter.interpreter(*argv)
    except RunTimeException as e:
        sys.stdout.write(f"Error: {e.msg}\n")
        exit(1)
    exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
