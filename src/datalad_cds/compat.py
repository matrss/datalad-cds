import sys


def removeprefix(s: str, prefix: str) -> str:
    if sys.version_info >= (3, 9):  # pragma: py-lt-39
        return s.removeprefix(prefix)
    else:  # pragma: py-gte-39
        if s.startswith(prefix):
            return s[len(prefix) :]
        return s
