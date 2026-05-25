import pytest

from semantic_context_server.application.dto.llm_request import LLMRequest

# ---------------------------------------------------------
# SUCESSO
# ---------------------------------------------------------


def test_create_with_required_fields():
    req = LLMRequest(
        prompt="hello",
        campaign_id="test",
    )

    assert req.prompt == "hello"
    assert req.temperature == 0.7
    assert req.max_tokens == 1000
    assert req.system_prompt is None
    assert req.timeout is None
    assert req.metadata == {}


def test_prompt_is_stripped():
    req = LLMRequest(
        prompt="  hello  ",
        campaign_id="test",
    )

    assert req.prompt == "hello"


def test_custom_values():
    req = LLMRequest(
        prompt="test",
        campaign_id="test",
        system_prompt="system",
        temperature=1.2,
        max_tokens=500,
        timeout=10.0,
        metadata={"a": 1},
    )

    assert req.system_prompt == "system"
    assert req.temperature == 1.2
    assert req.max_tokens == 500
    assert req.timeout == 10.0
    assert req.metadata == {"a": 1}


# ---------------------------------------------------------
# VALIDAÇÕES - PROMPT
# ---------------------------------------------------------


@pytest.mark.parametrize("invalid_prompt", ["", "   ", None])
def test_invalid_prompt_raises(invalid_prompt):
    with pytest.raises(ValueError):
        LLMRequest(
            prompt=invalid_prompt,
            campaign_id="test",
        )


# ---------------------------------------------------------
# VALIDAÇÕES - CAMPAIGN
# ---------------------------------------------------------


def test_missing_campaign_id_raises():
    with pytest.raises(ValueError):
        LLMRequest(
            prompt="ok",
            campaign_id="",
        )


# ---------------------------------------------------------
# VALIDAÇÕES - TEMPERATURE
# ---------------------------------------------------------


@pytest.mark.parametrize("invalid_temp", [-0.1, 2.1, 999])
def test_invalid_temperature_raises(invalid_temp):
    with pytest.raises(ValueError):
        LLMRequest(
            prompt="ok",
            campaign_id="test",
            temperature=invalid_temp,
        )


def test_temperature_bounds():
    LLMRequest(prompt="ok", campaign_id="test", temperature=0)
    LLMRequest(prompt="ok", campaign_id="test", temperature=2)


# ---------------------------------------------------------
# VALIDAÇÕES - TOKENS
# ---------------------------------------------------------


@pytest.mark.parametrize("invalid_tokens", [0, -1, -100])
def test_invalid_max_tokens_raises(invalid_tokens):
    with pytest.raises(ValueError):
        LLMRequest(
            prompt="ok",
            campaign_id="test",
            max_tokens=invalid_tokens,
        )


# ---------------------------------------------------------
# METADATA
# ---------------------------------------------------------


def test_metadata_is_not_shared_between_instances():
    r1 = LLMRequest(prompt="a", campaign_id="test")
    r2 = LLMRequest(prompt="b", campaign_id="test")

    r1.metadata["x"] = 1

    assert r2.metadata == {}
