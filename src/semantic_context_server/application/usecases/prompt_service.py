import json
from typing import Any

from semantic_context_server.application.ports.model_delegate import ModelDelegatePort
from semantic_context_server.shared.cache.cache import CacheManager


class PromptService:
    """Wraps a ModelDelegatePort with optional response caching."""

    def __init__(self, model_delegate: ModelDelegatePort, cache_manager: CacheManager) -> None:
        self.delegate = model_delegate
        self._cache = cache_manager

    async def generate(self, payload: dict[str, Any], background: Any = None) -> dict[str, Any]:
        cached = await self._cache.get(payload)
        if cached is not None:
            result: dict[str, Any] = json.loads(cached)
            return result

        response = await self.delegate.run(payload)
        await self._cache.set(payload, json.dumps(response).encode())
        return response
