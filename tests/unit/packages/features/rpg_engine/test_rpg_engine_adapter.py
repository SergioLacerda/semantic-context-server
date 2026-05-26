from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve()
while PROJECT_ROOT != PROJECT_ROOT.parent and not (PROJECT_ROOT / "pyproject.toml").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.features.rpg_engine import NarrativeUseCase  # noqa: E402


def test_rpg_engine_exports_narrative_usecase() -> None:
    assert NarrativeUseCase.__name__ == "NarrativeUseCase"
