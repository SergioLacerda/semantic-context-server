from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve()
while PROJECT_ROOT != PROJECT_ROOT.parent and not (PROJECT_ROOT / "pyproject.toml").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.narrative_server.app import create_app  # noqa: E402


def test_apps_narrative_server_create_app() -> None:
    app = create_app()
    assert app is not None
    assert app.title == "RPG Narrative Server"
