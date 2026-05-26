#!/usr/bin/env python3
"""Guard direct environment access outside config layer."""

from __future__ import annotations

import re
from pathlib import Path

SRC_ROOT = Path("src/semantic_context_server")
TEST_ROOT = Path("tests")

ALLOWED_FILES = {
    Path("src/semantic_context_server/infrastructure/runtime/execution/executor.py"),
    Path("tests/conftest.py"),
    Path("tests/runtime/test_signal_handlers.py"),
    Path("tests/unit/config/test_env_loader.py"),
}

ENV_PATTERNS = [
    re.compile(r"\bos\.getenv\s*\("),
    re.compile(r"\bos\.environ\s*\["),
    re.compile(r"\bos\.environ\.get\s*\("),
]


def file_allowed(path: Path) -> bool:
    if path in ALLOWED_FILES:
        return True
    return path.parts[:3] == ("src", "semantic_context_server", "config")


def main() -> int:
    candidates = list(SRC_ROOT.rglob("*.py")) + list(TEST_ROOT.rglob("*.py"))
    violations: list[str] = []

    for path in sorted(candidates):
        if "__pycache__" in path.parts or file_allowed(path):
            continue
        text = path.read_text(encoding="utf-8")
        for pat in ENV_PATTERNS:
            for m in pat.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                violations.append(f"{path}:{line}: direct env access outside config layer")

    if violations:
        print("FAIL: direct env access policy violations detected:")
        for v in violations:
            print(f" - {v}")
        return 1

    print("Env access boundary guard passed: no disallowed direct env access found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
