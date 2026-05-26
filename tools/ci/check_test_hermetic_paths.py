#!/usr/bin/env python3
"""Guard tests against productive path mutations/usages."""

from __future__ import annotations

from pathlib import Path

FORBIDDEN_SNIPPETS = (
    "data/",
    ".sdd/",
    ".analysis/",
)


def main() -> int:
    violations: list[str] = []
    for path in sorted(Path("tests").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in FORBIDDEN_SNIPPETS:
            if snippet in text:
                line = text.split(snippet, 1)[0].count("\n") + 1
                violations.append(f"{path}:{line}: forbidden productive path reference '{snippet}'")

    if violations:
        print("FAIL: hermetic test path policy violations detected:")
        for v in violations:
            print(f" - {v}")
        return 1

    print("Hermetic test path guard passed: no productive path references in tests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
