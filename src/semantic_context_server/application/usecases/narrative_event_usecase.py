import logging
from typing import Any

from semantic_context_server.application.contracts.response import Response
from semantic_context_server.application.dto.llm_request import LLMRequest
from semantic_context_server.domain.narrative.narrative_builder import NarrativeBuilder

logger = logging.getLogger(__name__)


class NarrativeUseCase:
    """
    Orquestrador principal da narrativa.

    ✔ Integra memória (RAG híbrido)
    ✔ Integra contexto externo (retrieval)
    ✔ Constrói prompt estruturado
    ✔ Garante robustez (fallbacks)
    """

    def __init__(
        self,
        llm: Any,
        memory_service: Any,
        context_builder: Any,
        context_service: Any = None,
        intent_classifier: Any = None,
        narrative_builder: Any = None,
    ) -> None:
        self.llm = llm
        self.memory = memory_service
        self.context_builder = context_builder
        self.context_service = context_service

        self.intent_classifier = intent_classifier or self._default_intent()
        self.narrative_builder = narrative_builder or NarrativeBuilder()

    # ==========================================================
    # DEFAULT INTENT
    # ==========================================================

    def _default_intent(self) -> Any:
        class DummyIntent:
            async def classify(self, *_: Any) -> str:
                return "DEFAULT"

        return DummyIntent()

    # ==========================================================
    # FALLBACK
    # ==========================================================

    def _fallback_response(self, action: str, intent: str) -> Response:
        return Response(
            text=f"O mundo reage à sua ação ('{action}'), mas algo permanece incerto...",
            type="narrative",
            metadata={"intent": intent, "fallback": True},
        )

    # ==========================================================
    # EXECUTE
    # ==========================================================

    async def execute(self, campaign_id: str, action: str, user_id: str) -> Response:
        logger.info("🎭 Narrative execution started")

        intent = await self.intent_classifier.classify(action, campaign_id)
        ctx, _ = await self.context_builder.build(
            campaign_id=campaign_id, action=action, intent=intent
        )

        mem_semantic = await self._enrich_from_memory(ctx, campaign_id, action)
        self._apply_context_fallback(ctx)
        ext_semantic = await self._enrich_from_external(campaign_id, action, intent)
        self._merge_semantic(ctx, mem_semantic, ext_semantic)

        request = self._build_llm_request(ctx, action, campaign_id, intent)

        try:
            response = await self.llm.generate(request)
        except Exception:
            logger.warning("LLM failed", exc_info=True)
            return self._fallback_response(action, intent)

        text = self._extract_text(response, self.narrative_builder)
        await self._write_memory(campaign_id, action, text)

        scene = ctx.get("scene_type")
        return Response(
            text=text, type="narrative", metadata={"intent": intent, "scene_type": scene}
        )

    async def _enrich_from_memory(self, ctx: dict, campaign_id: str, action: str) -> list[str]:
        if not self.memory:
            return []
        try:
            try:
                mem_ctx = await self.memory.get_context(campaign_id=campaign_id, query=action)
            except TypeError:
                mem_ctx = await self.memory.get_context(action)
            if mem_ctx.get("summary"):
                ctx["summary"] = mem_ctx["summary"]
            if mem_ctx.get("recent"):
                ctx["recent_events"] = (ctx.get("recent_events", []) + mem_ctx["recent"])[-5:]
            if mem_ctx.get("graph"):
                ctx["related_entities"] = mem_ctx["graph"]
            if mem_ctx.get("vector"):
                ctx["vector_context"] = mem_ctx["vector"]
            if mem_ctx.get("combined"):
                ctx["combined_context"] = mem_ctx["combined"]
            return mem_ctx.get("semantic") or []
        except Exception:
            logger.warning("Memory context failed", exc_info=True)
            return []

    def _apply_context_fallback(self, ctx: dict) -> None:
        if not ctx.get("summary") and not ctx.get("recent_events"):
            ctx["summary"] = "O ambiente ainda não foi explorado."

    async def _enrich_from_external(self, campaign_id: str, action: str, intent: str) -> list[str]:
        if not self.context_service:
            return []
        try:
            result: list[str] = await self.context_service.search(
                campaign_id=campaign_id, query=action, intent=intent
            )
            return result
        except Exception:
            logger.warning("ContextService failed", exc_info=True)
            return []

    def _merge_semantic(self, ctx: dict, mem: list[str], ext: list[str]) -> None:
        combined = (mem or []) + (ext or [])
        if combined:
            ctx["semantic"] = "\n".join(combined[:5])

    def _build_llm_request(
        self, ctx: dict, action: str, campaign_id: str, intent: str
    ) -> LLMRequest:
        builder = self.narrative_builder
        scene = ctx.get("scene_type")
        config = builder.get_generation_config(scene)
        return LLMRequest(
            prompt=builder.build_user_prompt(ctx=ctx, action=action),
            campaign_id=campaign_id,
            system_prompt=builder.build_system_prompt(scene_type=scene),
            temperature=config["temperature"],
            max_tokens=int(config["max_tokens"]),
            metadata={"intent": intent, "scene_type": scene},
        )

    def _extract_text(self, response: Any, builder: Any) -> str:
        if response is None:
            raise RuntimeError("LLM returned None")
        if getattr(response, "content", None) is None:
            raise RuntimeError("LLM returned empty content")
        try:
            text: str = builder.sanitize_output(response.content)
        except ValueError as e:
            raise RuntimeError("Invalid LLM output") from e
        if not text:
            raise RuntimeError("LLM returned empty content")
        return text

    async def _write_memory(self, campaign_id: str, action: str, text: str) -> None:
        if not self.memory:
            return
        try:
            try:
                await self.memory.append(campaign_id, f"USER: {action}")
                await self.memory.append(campaign_id, f"GM: {text}")
            except TypeError:
                await self.memory.append(f"USER: {action}")
                await self.memory.append(f"GM: {text}")
        except Exception:
            logger.warning("Memory write failed", exc_info=True)
