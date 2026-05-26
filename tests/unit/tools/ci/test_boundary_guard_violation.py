from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from packages.core.shared_kernel.text_io import write_text_utf8


def test_boundary_guard_fails_on_intentional_cross_feature_violation(tmp_path: Path) -> None:
    packages = tmp_path / "packages"
    feat_a = packages / "features" / "a"
    feat_b = packages / "features" / "b"
    feat_a.mkdir(parents=True)
    feat_b.mkdir(parents=True)

    write_text_utf8(feat_a / "__init__.py", "")
    write_text_utf8(feat_b / "__init__.py", "")

    write_text_utf8(feat_b / "internal.py", "X = 1\n")
    write_text_utf8(
        feat_a / "module.py",
        "from packages.features.b.internal import X\nVALUE = X\n",
    )

    script = Path("tools/ci/check_package_boundaries.py").resolve()
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "forbidden deep cross-feature import" in (result.stdout + result.stderr)


def test_boundary_guard_fails_on_legacy_import_regression(tmp_path: Path) -> None:
    packages = tmp_path / "packages"
    feat = packages / "features" / "a"
    feat.mkdir(parents=True)

    write_text_utf8(feat / "__init__.py", "")
    write_text_utf8(
        feat / "module.py",
        "from semantic_context_server.shared.text_io import write_text_utf8\n",
    )

    script = Path("tools/ci/check_package_boundaries.py").resolve()
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "forbidden legacy import" in (result.stdout + result.stderr)
