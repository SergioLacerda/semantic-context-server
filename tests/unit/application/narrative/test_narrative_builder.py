import pytest

from packages.features.prompt_engine_core.narrative_builder import NarrativeBuilder
from tests.utils.assertions import (
    assert_prompt_has,
    assert_prompt_semantic,
    assert_prompt_structure,
)


def build_prompt(builder, ctx, action):
    system = builder.build_system_prompt(ctx.get("scene_type"))
    user = builder.build_user_prompt(ctx=ctx, action=action)
    return f"{system}\n\n{user}"


def test_prompt_structure():
    builder = NarrativeBuilder()

    ctx = {
        "summary": "",
        "recent_events": ["contexto teste"],
        "retrieved": "",
        "related_entities": [],
        "scene_type": "DEFAULT",
    }

    prompt = build_prompt(builder, ctx=ctx, action="abrir porta")

    assert_prompt_structure(prompt)

    assert_prompt_has(
        prompt,
        "eventos recentes",
        "ação do jogador",
    )

    assert_prompt_semantic(
        prompt,
        "contexto teste",
        "abrir porta",
    )


def test_prompt_without_context():
    builder = NarrativeBuilder()

    ctx = {
        "summary": "",
        "recent_events": [],
        "retrieved": "",
        "related_entities": [],
        "scene_type": "DEFAULT",
    }

    prompt = build_prompt(builder, ctx=ctx, action="andar")

    assert_prompt_has(prompt, "ação do jogador")
    assert_prompt_semantic(prompt, "andar")


def test_system_prompt():
    builder = NarrativeBuilder()

    system = builder.build_system_prompt()

    assert "mestre de rpg" in system.lower()
    assert "ooc" in system.lower()


def test_user_prompt():
    builder = NarrativeBuilder()

    ctx = {
        "summary": "",
        "recent_events": ["x"],
        "retrieved": "",
        "related_entities": [],
        "scene_type": "DEFAULT",
    }

    user = builder.build_user_prompt(ctx=ctx, action="y")

    assert_prompt_has(user, "eventos recentes")
    assert_prompt_semantic(user, "x", "y")


def test_normalize_action():
    builder = NarrativeBuilder()

    result = builder.normalize_action(" atacar\ninimigo ")

    assert result == "atacar inimigo"


def test_enforce_length():
    builder = NarrativeBuilder()

    text = "a" * 5000

    result = builder.enforce_length(text, max_chars=100)

    assert len(result) == 100


def test_sanitize_output():
    builder = NarrativeBuilder()

    text = "\n linha1 \n\n linha2 \n"

    result = builder.sanitize_output(text)

    assert result == "linha1\nlinha2"


def test_sanitize_output_none():
    builder = NarrativeBuilder()

    with pytest.raises(ValueError):
        builder.sanitize_output(None)
