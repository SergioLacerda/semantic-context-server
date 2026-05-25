import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Any

from semantic_context_server.application.dto.llm_request import LLMRequest
from semantic_context_server.application.dto.llm_response import LLMResponse
from semantic_context_server.application.ports.llm import LLMServicePort
from semantic_context_server.shared.hash_utils import sha256_hash
from semantic_context_server.shared.resilience import resilient_call

logger = logging.getLogger(__name__)


class LLMService(LLMServicePort):
    def __init__(
        self,
        provider: Any,
        *,
        response_cache_manager: Any = None,
        response_cache: Any = None,
        context_service: Any = None,
        narrative_graph: Any = None,
        timeout: float = 180.0,
        circuit_breaker: Any = None,
    ) -> None:
        self.provider = provider
        self.response_cache_manager = response_cache_manager
        self.response_cache = response_cache
        self.context_service = context_service
        self.graph = narrative_graph
        self.timeout = timeout
        self.circuit_breaker = circuit_breaker

        # 🔥 inflight dedup
        self._inflight: dict[str, asyncio.Future[LLMResponse]] = {}

    # ==========================================================
    # CACHE
    # ==========================================================

    def _resolve_cache(self, request: LLMRequest) -> Any:
        if not self.response_cache_manager or not request.campaign_id:
            return None
        return self.response_cache_manager.get(f"campaign:{request.campaign_id}")

    def _cache_key(self, request: LLMRequest) -> str:
        return sha256_hash(
            {
                "campaign": request.campaign_id,
                "prompt": request.prompt.strip().lower(),
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "metadata": request.metadata,
            }
        )

    # ==========================================================
    # INTERNAL
    # ==========================================================

    def _ensure_response(self, data: Any) -> LLMResponse | None:
        if data is None:
            return None

        if isinstance(data, LLMResponse):
            return data

        if isinstance(data, dict):
            return LLMResponse.from_dict(data)

        logger.warning(f"Unexpected cache type: {type(data)}")
        return None

    def _normalize(self, raw: Any) -> str:
        if isinstance(raw, dict):
            return raw.get("content") or raw.get("text") or ""
        if isinstance(raw, str):
            return raw
        return str(raw)

    def _compute_timeout(self, request: LLMRequest) -> float:
        if request.timeout:
            return request.timeout

        if not request.max_tokens:
            return self.timeout

        dynamic = request.max_tokens * 0.3
        return max(30.0, min(dynamic, self.timeout))

    # ==========================================================
    # RAG ENRICHMENT
    # ==========================================================

    async def _build_prompt(self, request: LLMRequest) -> LLMRequest:
        prompt = request.prompt

        if self.context_service:
            try:
                context = await self.context_service.search(prompt)
                if context:
                    prompt = "[Contexto]\n" + "\n".join(context[:5]) + f"\n\n{prompt}"
            except Exception:
                logger.exception("Context enrichment failed")

        if self.graph:
            try:
                hint = await self.graph.build_hint(prompt)
                if hint:
                    prompt = f"{hint}\n\n{prompt}"
            except Exception:
                logger.exception("Graph hint failed")

        return request.copy_with(prompt=prompt)

    # ==========================================================
    # GENERATE
    # ==========================================================

    async def generate(self, request: LLMRequest) -> LLMResponse:
        if not request or not request.prompt:
            raise TypeError("LLMRequest must contain a prompt")
        if not request.campaign_id:
            raise ValueError("LLMRequest.campaign_id is required")

        request = await self._build_prompt(request)
        key = self._cache_key(request)

        existing = self._inflight.get(key)
        if existing:
            return await existing

        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._inflight[key] = future

        try:
            response = await self._resolve_from_cache(request, key)
            if response:
                future.set_result(response)
                return response

            response = await self._call_provider(request, key)
            future.set_result(response)
            return response

        except Exception as e:
            if self.circuit_breaker:
                self.circuit_breaker.failure()
            if not future.done():
                future.set_exception(e)
            raise

        finally:
            self._inflight.pop(key, None)

    async def _resolve_from_cache(self, request: LLMRequest, key: str) -> LLMResponse | None:
        if self.response_cache:
            cached = await self.response_cache.get(key)
            response = self._ensure_response(cached)
            if response:
                return response

        response_cache = self._resolve_cache(request)
        if response_cache:
            cached = await response_cache.get(key)
            response = self._ensure_response(cached)
            if response:
                if self.response_cache:
                    await self.response_cache.set(key, response.to_dict())
                return response

        return None

    async def _call_provider(self, request: LLMRequest, key: str) -> LLMResponse:
        if self.circuit_breaker and not self.circuit_breaker.allow():
            raise RuntimeError("LLM circuit open")

        raw = await resilient_call(
            self.provider.generate,
            request,
            timeout=self._compute_timeout(request),
        )
        if raw is None:
            raise RuntimeError("LLM returned None")

        response = LLMResponse(
            content=self._normalize(raw),
            provider=getattr(self.provider, "name", "unknown"),
            model=getattr(self.provider, "model", "unknown"),
        )
        if self.circuit_breaker:
            self.circuit_breaker.success()

        response_cache = self._resolve_cache(request)
        if self.response_cache:
            await self.response_cache.set(key, response.to_dict())
        if response_cache:
            await response_cache.set(key, response.to_dict())

        return response

    # ==========================================================
    # STREAM
    # ==========================================================

    async def stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        request = await self._build_prompt(request)
        key = self._cache_key(request)

        if self.response_cache:
            cached = await self.response_cache.get(key)
            response = self._ensure_response(cached)
            if response:
                yield response.content
                return

        collected = ""

        async for chunk in self.provider.stream(request):
            collected += chunk
            yield chunk

        if self.response_cache:
            await self.response_cache.set(
                key,
                LLMResponse(
                    content=collected,
                    provider=getattr(self.provider, "name", "unknown"),
                    model=getattr(self.provider, "model", "unknown"),
                    latency_ms=0,
                ).to_dict(),
            )
