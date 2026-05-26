#!/usr/bin/env python3
"""Unified lint and guardrail runner for Make targets."""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from shutil import which


def run_step(title: str, cmd: Sequence[str]) -> None:
    print(f"\\n== {title} ==")
    print("$", " ".join(cmd))
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def run_warn_step(title: str, cmd: Sequence[str]) -> None:
    print(f"\\n== {title} (warn-only) ==")
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=False)


def run_import_linter_guard() -> None:
    if which("lint-imports"):
        run_step("import-linter clean architecture guard", ["uv", "run", "lint-imports"])
        return

    probe = subprocess.run(["uv", "run", "python", "-m", "importlinter", "--help"], check=False)
    if probe.returncode == 0:
        run_step(
            "import-linter clean architecture guard",
            ["uv", "run", "python", "-m", "importlinter"],
        )
        return

    print("\n== import-linter clean architecture guard (warn-only) ==")
    print("WARN: lint-imports/importlinter not available in current environment; skipping import-linter gate.")


def run_lint_check() -> None:
    run_warn_step(
        "class size (>200 lines) advisory",
        ["uv", "run", "python", "tools/ci/check_class_size_warn.py", "--max-lines", "200"],
    )
    run_step("legacy ai path guard", ["uv", "run", "python", "tools/ci/check_no_legacy_ai_paths.py"])
    run_warn_step(
        "warning suppression guard",
        ["uv", "run", "python", "tools/ci/check_warning_suppressions.py"],
    )
    run_step(
        "text io centralization guard",
        ["uv", "run", "python", "tools/ci/check_text_io_centralization.py"],
    )
    run_step(
        "env access boundary guard",
        ["uv", "run", "python", "tools/ci/check_env_access_boundaries.py"],
    )
    run_step(
        "hermetic test path guard",
        ["uv", "run", "python", "tools/ci/check_test_hermetic_paths.py"],
    )
    run_step("import cycle guard", ["uv", "run", "python", "tools/ci/check_import_cycles.py"])
    run_step(
        "package boundary guard",
        ["uv", "run", "python", "tools/ci/check_package_boundaries.py"],
    )
    run_import_linter_guard()
    # Ruff F401/F841 break on unused imports/locals; lint-fix applies auto-fix when possible.
    run_step("ruff check", ["uv", "run", "ruff", "check", "src", "tests"])
    run_step("ruff format --check", ["uv", "run", "ruff", "format", "--check", "src", "tests"])
    run_step("mypy", ["uv", "run", "mypy", "src"])
    run_step("architecture tests", ["uv", "run", "pytest", "-m", "architecture"])
    run_step("contract tests", ["uv", "run", "pytest", "-m", "contract"])


def run_lint_fix() -> None:
    run_step("ruff check --fix", ["uv", "run", "ruff", "check", "--fix", "src", "tests"])
    run_step("ruff format", ["uv", "run", "ruff", "format", "src", "tests"])
    # Re-validate the full gate after applying fixes.
    run_lint_check()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run lint and guardrail checks")
    parser.add_argument("mode", choices=["check", "fix"], help="Execution mode")
    args = parser.parse_args(argv)

    if args.mode == "check":
        run_lint_check()
    else:
        run_lint_fix()

    print("\\nLint pipeline completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
