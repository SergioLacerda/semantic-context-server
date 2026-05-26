from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve()
while PROJECT_ROOT != PROJECT_ROOT.parent and not (PROJECT_ROOT / "pyproject.toml").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.features.prompt_engine_core import NarrativeBuilder, SessionSummarizer  # noqa: E402


def test_narrative_builder_builds_prompt_sections() -> None:
    builder = NarrativeBuilder()
    prompt = builder.build_user_prompt(
        {
            "summary": "Resumo",
            "recent_events": ["evento 1", "evento 2"],
            "vector_context": ["mem1"],
        },
        "abrir a porta",
    )

    assert "[Contexto narrativo]" in prompt
    assert "[Ação do jogador]" in prompt
    assert "abrir a porta" in prompt


def test_narrative_builder_sanitize_output() -> None:
    builder = NarrativeBuilder()
    raw = '" linha 1\n\nlinha 2 "'
    assert builder.sanitize_output(raw) == "linha 1\nlinha 2"


def test_session_summarizer_extract_and_prompt() -> None:
    summarizer = SessionSummarizer()
    extracted = summarizer.extract(
        [
            {"type": "USER", "text": "Ataco o goblin"},
            {"type": "GM", "text": "O goblin recua"},
        ]
    )
    assert "[Jogador]" in extracted
    assert "[Mestre]" in extracted

    prompt = summarizer.build_prompt(extracted)
    assert "Sua tarefa é condensar a sessão" in prompt
