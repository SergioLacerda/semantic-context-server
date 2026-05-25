import difflib
from pathlib import Path

from tests.config.helpers.io import read_text_utf8, write_text_utf8


def normalize(s: str) -> str:
    return "\n".join(line.rstrip() for line in s.strip().splitlines())


def diff_strings(expected: str, actual: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            normalize(expected),
            normalize(actual),
            fromfile="expected",
            tofile="actual",
            lineterm="",
        )
    )


def assert_golden(path: Path, actual: str, update: bool = False):
    if update:
        write_text_utf8(path, actual)
        return

    expected = read_text_utf8(path)

    if normalize(expected) != normalize(actual):
        diff = diff_strings(expected, actual)

        raise AssertionError(f"\n\n❌ GOLDEN MISMATCH: {path.name}\n\n{diff}\n")
