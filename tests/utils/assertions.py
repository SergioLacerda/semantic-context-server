# tests/utils/assertions.py

from semantic_context_server.application.contracts.response import Response
from semantic_context_server.domain.narrative.narrative_builder import NarrativeBuilder
from tests.config.helpers.golden_assert import normalize

# ==========================================================
# BASE
# ==========================================================


def assert_response(resp):
    assert isinstance(resp, Response), f"Expected Response, got {type(resp)}"
    assert isinstance(resp.text, str), "Response.text must be string"


def assert_not_empty(resp):
    assert_response(resp)
    assert resp.text.strip() != "", "Response is empty"


def assert_contains(resp, text: str):
    """
    ⚠️ LEGACY (manter por compatibilidade)
    """
    assert_response(resp)
    assert text in resp.text, f"Expected '{text}' in:\n{resp.text}"


def assert_any_contains(text: str, keywords: list[str]):
    """
    ✔ usado em testes antigos (string pura)
    """
    text_lower = text.lower()

    assert any(k.lower() in text_lower for k in keywords), f"Expected one of {keywords} in:\n{text}"


# ==========================================================
# LLM / SEMANTIC ASSERTIONS (🔥 PRINCIPAL)
# ==========================================================


def assert_semantic(resp, *keywords):
    """
    ✔ valida presença semântica (resiliente a LLM)
    """
    assert_response(resp)

    text = resp.text.lower()

    assert any(k.lower() in text for k in keywords), (
        f"\nExpected one of {keywords}\nGot:\n{resp.text}"
    )


def assert_not_contains_semantic(resp, *keywords):
    """
    ✔ garante ausência de termos
    """
    assert_response(resp)

    text = resp.text.lower()

    assert all(k.lower() not in text for k in keywords), (
        f"\nUnexpected keywords {keywords}\nGot:\n{resp.text}"
    )


def assert_min_length(resp, min_words=3):
    """
    ✔ evita respostas pobres ou vazias
    """
    assert_response(resp)

    words = resp.text.split()

    assert len(words) >= min_words, f"Too short response ({len(words)} words):\n{resp.text}"


def assert_semantic_all(resp, *keywords):
    """
    ✔ garante que TODOS os termos aparecem
    (útil para validação mais forte)
    """
    assert_response(resp)

    text = resp.text.lower()

    assert all(k.lower() in text for k in keywords), (
        f"\nExpected ALL of {keywords}\nGot:\n{resp.text}"
    )


# ==========================================================
# PROMPT ASSERTIONS (RAG / STRUCTURE)
# ==========================================================


def assert_prompt_structure(prompt: str):
    text = prompt.lower()

    assert "você é um mestre de rpg" in text, "Missing system prompt"
    assert "ação do jogador" in text, "Missing player action"
    assert "descreva o que acontece a seguir" in text, "Missing instruction"


def assert_prompt_has(prompt: str, *sections):
    text = prompt.lower()

    for s in sections:
        assert s.lower() in text, f"Missing '{s}' in:\n{prompt}"


def assert_prompt_not_has(prompt: str, *sections):
    text = prompt.lower()

    for s in sections:
        assert s.lower() not in text, f"Unexpected '{s}' in:\n{prompt}"


def assert_prompt_semantic(prompt: str, *keywords):
    text = prompt.lower()

    assert any(k.lower() in text for k in keywords), f"\nExpected one of {keywords}\nGot:\n{prompt}"


def assert_prompt_block(prompt: str, block_name: str):
    text = prompt.lower()

    assert block_name.lower() in text, f"Missing block '{block_name}' in:\n{prompt}"


def assert_prompt_blocks(prompt: str, *blocks):
    """
    ✔ valida múltiplos blocos importantes
    """
    text = prompt.lower()

    for block in blocks:
        assert block.lower() in text, f"Missing block '{block}' in:\n{prompt}"


def assert_prompt_contains(prompt: str, *keywords):
    text = prompt.lower()
    for k in keywords:
        assert k.lower() in text, f"Missing '{k}' in prompt:\n{prompt}"


def build_prompt(ctx: dict, action: str) -> str:
    builder = NarrativeBuilder()

    system = builder.build_system_prompt(str(ctx.get("scene_type") or "DEFAULT"))

    user = builder.build_user_prompt(
        ctx=ctx,
        action=action,
    )

    return normalize(f"{system}\n\n{user}")


# ==========================================================
# OPTIONAL DSL (🔥 MELHOR UX)
# ==========================================================


class ExpectResponse:
    def __init__(self, resp):
        assert_response(resp)
        self.text = resp.text.lower()

    def to_contain(self, *keywords):
        assert any(k.lower() in self.text for k in keywords), (
            f"Expected one of {keywords}\nGot:\n{self.text}"
        )
        return self

    def has(self, *keywords):
        """
        alias mais semântico
        """
        return self.to_contain(*keywords)

    def not_to_contain(self, *keywords):
        assert all(k.lower() not in self.text for k in keywords), (
            f"Unexpected keywords {keywords}\nGot:\n{self.text}"
        )
        return self

    def min_length(self, n=3):
        assert len(self.text.split()) >= n, (
            f"Too short ({len(self.text.split())} words):\n{self.text}"
        )
        return self


def expect(resp):
    return ExpectResponse(resp)
