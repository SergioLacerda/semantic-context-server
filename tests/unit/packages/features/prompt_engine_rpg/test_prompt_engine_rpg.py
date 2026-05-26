from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve()
while PROJECT_ROOT != PROJECT_ROOT.parent and not (PROJECT_ROOT / "pyproject.toml").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.features.prompt_engine_rpg import RPGPromptEngine  # noqa: E402


def test_rpg_prompt_engine_extends_core_prompt() -> None:
    engine = RPGPromptEngine()

    system = engine.build_system_prompt(scene_type="COMBAT")
    assert "Mantenha continuidade" in system

    user = engine.build_user_prompt({"summary": "Resumo"}, "atacar")
    assert "[Diretriz RPG]" in user
    assert "atacar" in user


def test_rpg_prompt_engine_build_request() -> None:
    engine = RPGPromptEngine()
    req = engine.build_narrative_request({"summary": "ok"}, "explorar", scene_type="EXPLORATION")

    assert "system_prompt" in req
    assert "prompt" in req
    assert "explorar" in req["prompt"]
