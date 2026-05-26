from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRS = [
    Path("apps/narrative_server"),
    Path("packages/core/shared_kernel"),
    Path("packages/features/rpg_engine"),
    Path("packages/features/prompt_engine_core"),
    Path("packages/features/prompt_engine_rpg"),
    Path("packages/features/vector_index"),
    Path("packages/features/benchmark_engine"),
    Path("packages/features/llm_gateway"),
    Path("packages/features/embedding_gateway"),
    Path("packages/features/semantic_cache"),
    Path("packages/features/storage"),
    Path("packages/interfaces/http_api"),
    Path("packages/interfaces/discord_bot"),
]


@pytest.mark.architecture
def test_wave1_scaffold_exists() -> None:
    missing = [str(path) for path in REQUIRED_DIRS if not (PROJECT_ROOT / path).exists()]
    assert not missing, "Missing Wave 1 scaffold paths:\n" + "\n".join(missing)


@pytest.mark.architecture
def test_wave1_importable_dirs_follow_snake_case() -> None:
    roots = [PROJECT_ROOT / "apps", PROJECT_ROOT / "packages"]
    errors: list[str] = []

    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_dir():
                continue
            if path.name.startswith(".") or path.name == "__pycache__":
                continue
            if any(ch in path.name for ch in "-"):
                errors.append(str(path.relative_to(PROJECT_ROOT)))

    assert not errors, "Non-snake-case importable directories found:\n" + "\n".join(errors)


@pytest.mark.architecture
def test_wave1_boundary_matrix_artifacts_exist() -> None:
    required = [
        PROJECT_ROOT / "docs/architecture/modular-monolith-boundaries.md",
        PROJECT_ROOT / "tools/architecture/import-boundary-matrix.yaml",
    ]
    missing = [str(p.relative_to(PROJECT_ROOT)) for p in required if not p.exists()]
    assert not missing, "Missing boundary artifacts:\n" + "\n".join(missing)


@pytest.mark.architecture
@pytest.mark.parametrize(
    "guard_script",
    [
        "tools/ci/check_package_boundaries.py",
        "tools/ci/check_env_access_boundaries.py",
        "tools/ci/check_test_hermetic_paths.py",
    ],
)
def test_wave1_guard_scripts_pass(guard_script: str) -> None:
    cmd = [sys.executable, str(PROJECT_ROOT / guard_script)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert result.returncode == 0, (
        f"Guard failed: {guard_script}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
