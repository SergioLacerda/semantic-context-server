#!/usr/bin/env python3
"""Warn when Python classes exceed configured line threshold."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path

DEFAULT_MAX_LINES = 200
ROOTS = ("src", "tests")


def iter_python_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for root in ROOTS:
        base = repo_root / root
        if not base.exists():
            continue
        files.extend(path for path in base.rglob("*.py") if "__pycache__" not in path.parts)
    return files


def class_span(node: ast.ClassDef) -> int:
    end_lineno = getattr(node, "end_lineno", node.lineno)
    return end_lineno - node.lineno + 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Warn for oversized classes")
    parser.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    violations: list[str] = []

    for py_file in iter_python_files(repo_root):
        source = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            span = class_span(node)
            if span > args.max_lines:
                rel = py_file.relative_to(repo_root).as_posix()
                violations.append(
                    f"{rel}:{node.lineno}: class '{node.name}' has {span} lines (> {args.max_lines})"
                )

    if violations:
        print("WARNING: oversized classes detected:")
        for item in violations:
            print(f" - {item}")
        return 0

    print("Class size guard passed: no class exceeds max line threshold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
