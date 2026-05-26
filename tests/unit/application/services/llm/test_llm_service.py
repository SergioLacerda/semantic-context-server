from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from packages.features.llm_gateway.application.circuit_breaker import CircuitBreaker
from packages.features.llm_gateway.application.llm_service import LLMService
from semantic_context_server.application.dto.llm_request import LLMRequest
from semantic_context_server.application.dto.llm_response import LLMResponse

# ==========================================================
# HELPERS
# ==========================================================


def make_request(**kwargs) -> LLMRequest:
    data = {
        "prompt": kwargs.get("prompt", "hi"),
        "system_prompt": kwargs.get("system_prompt"),
        "temperature": kwargs.get("temperature", 0.5),
        "campaign_id": kwargs.get("campaign_id", "test"),
    }

    if "max_tokens" in kwargs and kwargs["max_tokens"] is not None:
        data["max_tokens"] = kwargs["max_tokens"]

    if "metadata" in kwargs and kwargs["metadata"] is not None:
        data["metadata"] = kwargs["metadata"]

    if "tools" in kwargs and kwargs["tools"] is not None:
        data["tools"] = kwargs["tools"]

    return LLMRequest(**data)


def make_response(content="ok"):
    return LLMResponse(
        content=content,
        provider="test",
        model="test",
    )


# ==========================================================
# CORE
# ==========================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_calls_provider():
    with patch(
        "packages.features.llm_gateway.application.llm_service.resilient_call",
        new=AsyncMock(return_value="ok"),
    ):
        service = LLMService(provider=MagicMock())

        result = await service.generate(make_request())

    assert result.content == "ok"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_empty_response():
    with patch(
        "packages.features.llm_gateway.application.llm_service.resilient_call",
        new=AsyncMock(return_value=""),
    ):
        service = LLMService(provider=MagicMock())

        result = await service.generate(make_request())

    assert result.content == ""


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_returns_none_raises():
    class Provider:
        async def generate(self, req):
            return None

    service = LLMService(provider=Provider())

    with pytest.raises(RuntimeError):
        await service.generate(make_request())


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_exception():
    with patch(
        "packages.features.llm_gateway.application.llm_service.resilient_call",
        new=AsyncMock(side_effect=ValueError("fail")),
    ):
        service = LLMService(provider=MagicMock())

        with pytest.raises(ValueError):
            await service.generate(make_request())


# ==========================================================
# CACHE
# ==========================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_l1_cache_hit():
    ttl_cache = MagicMock()
    ttl_cache.get = AsyncMock(return_value=make_response("cached"))
    ttl_cache.set = AsyncMock()

    service = LLMService(provider=MagicMock(), response_cache=ttl_cache)

    result = await service.generate(make_request())

    assert result.content == "cached"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_l2_cache_hit():
    ttl_cache = MagicMock()
    ttl_cache.get = AsyncMock(return_value=None)
    ttl_cache.set = AsyncMock()

    response_cache = MagicMock()
    response_cache.get = AsyncMock(return_value=make_response("cached_l2"))
    response_cache.set = AsyncMock()

    manager = MagicMock()
    manager.get.return_value = response_cache

    service = LLMService(
        provider=MagicMock(),
        response_cache=ttl_cache,
        response_cache_manager=manager,
    )

    result = await service.generate(make_request())

    assert result.content == "cached_l2"
    ttl_cache.set.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_sets_caches():
    ttl_cache = MagicMock()
    ttl_cache.get = AsyncMock(return_value=None)
    ttl_cache.set = AsyncMock()

    response_cache = MagicMock()
    response_cache.get = AsyncMock(return_value=None)
    response_cache.set = AsyncMock()

    manager = MagicMock()
    manager.get.return_value = response_cache

    with patch(
        "packages.features.llm_gateway.application.llm_service.resilient_call",
        new=AsyncMock(return_value="ok"),
    ):
        service = LLMService(
            provider=MagicMock(),
            response_cache=ttl_cache,
            response_cache_manager=manager,
        )

        result = await service.generate(make_request())

    assert result.content == "ok"
    ttl_cache.set.assert_called_once()
    response_cache.set.assert_called_once()


# ==========================================================
# CIRCUIT BREAKER
# ==========================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_circuit_open_blocks_call():
    cb = CircuitBreaker(failure_threshold=1)
    cb.failure()

    service = LLMService(
        provider=MagicMock(),
        circuit_breaker=cb,
    )

    with pytest.raises(RuntimeError):
        await service.generate(make_request())


@pytest.mark.unit
@pytest.mark.asyncio
async def test_success_resets_circuit():
    cb = CircuitBreaker(failure_threshold=1)

    with patch(
        "packages.features.llm_gateway.application.llm_service.resilient_call",
        new=AsyncMock(return_value="ok"),
    ):
        service = LLMService(
            provider=MagicMock(),
            circuit_breaker=cb,
        )

        result = await service.generate(make_request())

    assert result.content == "ok"
    assert cb.state == "CLOSED"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_failure_triggers_circuit():
    cb = CircuitBreaker(failure_threshold=1)

    with patch(
        "packages.features.llm_gateway.application.llm_service.resilient_call",
        new=AsyncMock(side_effect=ValueError()),
    ):
        service = LLMService(
            provider=MagicMock(),
            circuit_breaker=cb,
        )

        with pytest.raises(ValueError):
            await service.generate(make_request())

    assert cb.state == "OPEN"


# ==========================================================
# CACHE KEY
# ==========================================================


@pytest.mark.unit
def test_cache_key_deterministic():
    service = LLMService(provider=MagicMock())

    req1 = make_request(prompt="hello")
    req2 = make_request(prompt="hello")

    assert service._cache_key(req1) == service._cache_key(req2)


@pytest.mark.unit
def test_cache_key_changes():
    service = LLMService(provider=MagicMock())

    req1 = make_request(prompt="hello", temperature=0.0)
    req2 = make_request(prompt="hello", temperature=1.0)

    assert service._cache_key(req1) != service._cache_key(req2)


def test_cache_key_with_metadata():
    service = LLMService(provider=MagicMock())

    req = make_request(
        metadata={"a": 1},
    )

    key = service._cache_key(req)

    assert isinstance(key, str)


# ==========================================================
# TIMEOUT
# ==========================================================


@pytest.mark.unit
def test_compute_timeout_dynamic():
    service = LLMService(provider=MagicMock(), timeout=60)

    req = make_request(max_tokens=100)

    result = service._compute_timeout(req)

    assert result <= 60
    assert result >= 30


@pytest.mark.unit
def test_compute_timeout_default():
    service = LLMService(provider=MagicMock(), timeout=60)

    req = make_request(max_tokens=None)

    assert service._compute_timeout(req) == 60


# ==========================================================
# STREAM
# ==========================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stream():
    class Provider:
        async def stream(self, request):
            yield "chunk"

    svc = LLMService(Provider())

    chunks = []
    async for c in svc.stream(make_request()):
        chunks.append(c)

    assert chunks == ["chunk"]
