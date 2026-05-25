"""Centralized UTF-8 text I/O helpers.

Use these helpers instead of direct `open(..., encoding=...)`,
`Path.read_text(...)`, or `Path.write_text(...)` across the codebase.
"""

from __future__ import annotations

from pathlib import Path


def read_text_utf8(path: Path, *, errors: str = "strict") -> str:
    with path.open("r", encoding="utf-8", errors=errors) as f:
        return f.read()


def write_text_utf8(path: Path, content: str, *, errors: str = "strict") -> None:
    with path.open("w", encoding="utf-8", errors=errors) as f:
        f.write(content)


def append_text_utf8(path: Path, content: str, *, errors: str = "strict") -> None:
    with path.open("a", encoding="utf-8", errors=errors) as f:
        f.write(content)
