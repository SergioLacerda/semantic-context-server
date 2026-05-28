# tests/test_prompt_caching.py
"""Tests for the LRU+disk caching system and PromptService.
These tests use a mock model delegate to avoid external API calls.
"""

import asyncio
from pathlib import Path

import pytest

from semantic_context_server.application.ports.model_delegate import ModelDelegatePort
from semantic_context_server.application.usecases.prompt_service import PromptService
from semantic_context_server.shared.cache.cache import CacheManager


# ---------------------------------------------------------------------------
# Mock delegate – returns a deterministic payload
# ---------------------------------------------------------------------------
class MockDelegate(ModelDelegatePort):
    async def run(self, payload: dict) -> dict:
        # Simulate a tiny async delay
        await asyncio.sleep(0.01)
        return {
            "prompt": f"generated:{payload['input']}",
            "model": payload.get("model", "mock"),
        }


@pytest.fixture(scope="function")
def cache_manager(tmp_path: Path) -> CacheManager:
    # Override the disk cache base_path to a temporary directory for isolation
    from packages.core.runtime_config.models import settings

    original_path = settings.cache.disk.base_path
    settings.cache.disk.base_path = str(tmp_path / "cache")
    cm = CacheManager()
    yield cm
    # cleanup / restore settings
    settings.cache.disk.base_path = original_path


@pytest.fixture(scope="function")
def prompt_service(cache_manager: CacheManager) -> PromptService:
    delegate = MockDelegate()
    return PromptService(delegate, cache_manager)


@pytest.mark.asyncio
async def test_lru_cache_round_trip(cache_manager: CacheManager):
    payload = {"input": "hello", "model": "local"}
    data = b'{"prompt": "generated:hello"}'  # simple JSON bytes

    # Ensure miss first
    assert await cache_manager.get(payload) is None

    # Store
    await cache_manager.set(payload, data)

    # Retrieve – should hit LRU (no disk read)
    result = await cache_manager.get(payload)
    assert result == data

    # Validate that the file also exists on disk
    from semantic_context_server.shared.cache.cache import _hash_request

    key = _hash_request(payload)
    disk_path = cache_manager._disk_path_for(key)
    assert disk_path.is_file()


@pytest.mark.asyncio
async def test_prompt_service_caching(prompt_service: PromptService, cache_manager: CacheManager):
    payload = {"input": "test", "model": "local"}

    # First call – cache miss, should invoke mock delegate
    result1 = await prompt_service.generate(payload, background=None)
    assert result1["prompt"] == "generated:test"

    # Second call – should be served from cache (no delegate call)
    # To verify, replace the delegate with one that raises if called
    class FailDelegate(ModelDelegatePort):
        async def run(self, payload: dict) -> dict:
            raise AssertionError("Delegate should not be called on cache hit")

    prompt_service.delegate = FailDelegate()
    result2 = await prompt_service.generate(payload, background=None)
    assert result2 == result1

    # Ensure the underlying cache contains the entry
    cached = await cache_manager.get(payload)
    assert cached is not None

    # Cleanup: prune old entries (should keep the current one)
    await cache_manager.prune()
    # After prune, the entry should still exist because TTL not exceeded
    assert await cache_manager.get(payload) is not None
