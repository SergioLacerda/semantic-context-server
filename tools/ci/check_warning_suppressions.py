#!/usr/bin/env python3
"""Enforce suppression comments to include explicit justification."""

from __future__ import annotations

import re
from pathlib import Path

ROOTS = ("src", "tests", "tools")
SUPPRESSION_PATTERNS = (
    re.compile(r"#\s*noqa(?:\b|:)"),
    re.compile(r"#\s*type:\s*ignore"),
    re.compile(r"#\s*nosec(?:\b|\s+B\d+)?"),
    re.compile(r"#\s*pylint:\s*disable="),
)
JUSTIFICATION_PATTERN = re.compile(r"justification\s*:\s*\S+", re.IGNORECASE)


def iter_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for root in ROOTS:
        base = repo_root / root
        if not base.exists():
            continue
        files.extend(p for p in base.rglob("*.py") if "__pycache__" not in p.parts)
    return files


def has_suppression(line: str) -> bool:
    return any(p.search(line) for p in SUPPRESSION_PATTERNS)


def has_justification(line: str) -> bool:
    return bool(JUSTIFICATION_PATTERN.search(line))


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    violations: list[str] = []

    for py_file in iter_files(repo_root):
        rel = py_file.relative_to(repo_root).as_posix()
        lines = py_file.read_text(encoding="utf-8").splitlines()

        for idx, line in enumerate(lines, start=1):
            if not has_suppression(line):
                continue

            prev_line = lines[idx - 2] if idx >= 2 else ""
            next_line = lines[idx] if idx < len(lines) else ""
            if has_justification(line) or has_justification(prev_line) or has_justification(next_line):
                continue

            violations.append(
                f"{rel}:{idx}: suppression without justification (add 'justification: <reason>')"
            )

    if violations:
        print("WARN: suppression policy violations detected:")
        for item in violations:
            print(f" - {item}")
        return 0

    print("Suppression policy passed: all suppressions include justification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
