import pytest

import semantic_context_server.infrastructure.adapters.llm as providers_mod
from semantic_context_server.application.dto.llm_request import LLMRequest
from semantic_context_server.application.services.llm.llm_errors import (
    LLMClientError,
    LLMRetryableError,
)
from semantic_context_server.infrastructure.adapters.llm.base_provider import BaseProvider
from semantic_context_server.infrastructure.adapters.llm.deepseek_provider import (
    DeepSeekProvider,
)
from semantic_context_server.infrastructure.adapters.llm.lmstudio_provider import LMStudioProvider
from semantic_context_server.infrastructure.adapters.llm.ollama_provider import OllamaProvider
from semantic_context_server.infrastructure.adapters.llm.openai_provider import OpenAIProvider
from tests.config.fakes.infrastructure.llm.fake_responses import (
    FakeOllamaResponse,
    FakeResponseEmpty,
    FakeResponseOpenAI,
)


def make_provider(provider_cls, *, model="test"):
    provider = provider_cls.__new__(provider_cls)

    if provider_cls is OpenAIProvider:
        BaseProvider.__init__(provider, "openai", model)
    elif provider_cls is LMStudioProvider:
        BaseProvider.__init__(provider, "lmstudio", model)
    elif provider_cls is DeepSeekProvider:
        BaseProvider.__init__(provider, "deepseek", model)
    elif provider_cls is OllamaProvider:
        BaseProvider.__init__(provider, "ollama", model)
    else:
        raise ValueError(f"Unsupported provider: {provider_cls}")

    return provider


@pytest.mark.asyncio
async def test_provider_success(monkeypatch):
    provider = make_provider(OpenAIProvider, model="test")

    async def fake_call(*args, **kwargs):
        return FakeResponseOpenAI("hello")

    monkeypatch.setattr(provider, "_call_api", fake_call)

    req = LLMRequest(prompt="hi", campaign_id="test")

    result = await provider.generate(req)

    assert result.content == "hello"


@pytest.mark.asyncio
async def test_provider_empty_response(monkeypatch):
    provider = make_provider(OpenAIProvider, model="test")

    async def fake_call(*args, **kwargs):
        return FakeResponseEmpty()

    monkeypatch.setattr(provider, "_call_api", fake_call)

    req = LLMRequest(prompt="hi", campaign_id="test")

    with pytest.raises(LLMRetryableError):
        await provider.generate(req)


@pytest.mark.asyncio
async def test_provider_generic_error(monkeypatch):
    provider = make_provider(OpenAIProvider, model="test")

    async def fake_call(*args, **kwargs):
        raise Exception("boom")

    monkeypatch.setattr(provider, "_call_api", fake_call)

    req = LLMRequest(prompt="hi", campaign_id="test")

    with pytest.raises(LLMRetryableError):
        await provider.generate(req)


@pytest.mark.asyncio
async def test_provider_client_error(monkeypatch):
    provider = make_provider(OpenAIProvider, model="test")

    async def fake_call(*args, **kwargs):
        raise ValueError("bad request")

    monkeypatch.setattr(provider, "_call_api", fake_call)

    req = LLMRequest(prompt="hi", campaign_id="test")

    with pytest.raises(LLMClientError):
        await provider.generate(req)


@pytest.mark.asyncio
async def test_ollama_response(monkeypatch):
    provider = make_provider(OllamaProvider, model="x")

    async def fake_call(*args, **kwargs):
        return FakeOllamaResponse("dragon")

    monkeypatch.setattr(provider, "_call_api", fake_call)

    req = LLMRequest(prompt="hi", campaign_id="test")

    result = await provider.generate(req)

    assert result.content == "dragon"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "provider_cls,kwargs",
    [
        ("OpenAIProvider", {"api_key": "x", "model": "m"}),
        ("LMStudioProvider", {"base_url": "http://x", "model": "m"}),
        ("DeepSeekProvider", {"api_key": "x", "model": "m"}),
    ],
)
async def test_all_providers_success(monkeypatch, provider_cls, kwargs):
    cls = getattr(providers_mod, provider_cls)
    provider = make_provider(cls, model=kwargs["model"])

    async def fake_call(*args, **kwargs):
        return FakeResponseOpenAI("ok")

    monkeypatch.setattr(provider, "_call_api", fake_call)

    result = await provider.generate(LLMRequest(prompt="test", campaign_id="test"))

    assert result.content == "ok"


@pytest.mark.asyncio
async def test_lmstudio_success(monkeypatch):
    provider = make_provider(LMStudioProvider, model="m")

    class FakeResp:
        choices = [type("obj", (), {"message": type("msg", (), {"content": "ok"})})]

    fake_client = type(
        "FakeClient",
        (),
        {
            "chat": type(
                "FakeChat",
                (),
                {
                    "completions": type("FakeCompletions", (), {})(),
                },
            )(),
        },
    )()

    async def fake_create(*args, **kwargs):
        return FakeResp()

    monkeypatch.setattr(fake_client.chat.completions, "create", fake_create, raising=False)
    provider.client = fake_client

    result = await provider.generate(LLMRequest(prompt="test", campaign_id="test"))

    assert result.content == "ok"
