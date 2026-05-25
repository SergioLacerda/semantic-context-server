#!/usr/bin/env python3
"""Enforce centralized text I/O usage via shared text_io helpers."""

from __future__ import annotations

import ast
from pathlib import Path

ROOTS = ("src", "tests")
ALLOWED_CALLER_SUFFIXES = {
    "src/semantic_context_server/shared/text_io.py",
    "tests/config/helpers/io.py",
    "tools/ci/check_text_io_centralization.py",
}


def iter_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for root in ROOTS:
        base = repo_root / root
        if not base.exists():
            continue
        files.extend(p for p in base.rglob("*.py") if "__pycache__" not in p.parts)
    return files


def is_allowed(path: Path, repo_root: Path) -> bool:
    rel = path.relative_to(repo_root).as_posix()
    return rel in ALLOWED_CALLER_SUFFIXES


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    violations: list[str] = []

    for py_file in iter_files(repo_root):
        if is_allowed(py_file, repo_root):
            continue

        source = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        rel = py_file.relative_to(repo_root).as_posix()

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            # open(...)
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                violations.append(f"{rel}:{node.lineno}: direct open() forbidden; use shared.text_io helpers")
                continue

            # path.read_text(...) / path.write_text(...)
            if isinstance(node.func, ast.Attribute) and node.func.attr in {"read_text", "write_text"}:
                violations.append(
                    f"{rel}:{node.lineno}: direct Path.{node.func.attr}() forbidden; use shared.text_io helpers"
                )

    if violations:
        print("FAIL: text I/O centralization violations detected:")
        for item in violations:
            print(f" - {item}")
        return 1

    print("Text I/O centralization passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
