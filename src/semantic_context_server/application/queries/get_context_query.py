from typing import Any


class GetContextQuery:
    def __init__(self, campaign_id: str):
        self.campaign_id = campaign_id


class GetContextQueryHandler:
    def __init__(
        self,
        memory_service: Any,
        context_service: Any,
        cache: Any = None,
    ) -> None:
        self.memory = memory_service
        self.context_service = context_service
        self.cache = cache

    async def handle(self, query: GetContextQuery, ctx: Any = None) -> str:
        campaign_id = query.campaign_id

        cache_key = f"campaign:{campaign_id}:context:v1"

        # ======================================================
        # CACHE
        # ======================================================
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return str(cached)

        # ======================================================
        # MEMORY (short + long term)
        # ======================================================
        memory = await self.memory.load_memory(campaign_id)

        summary = memory.summary()
        events = memory.get_recent_events()

        # ======================================================
        # SEMANTIC CONTEXT (RAG)
        # ======================================================
        semantic = []

        try:
            semantic = await self.context_service.search(
                query="context",
                k=3,
                campaign_id=campaign_id,
            )
        except Exception:
            # ideal: plugar logger aqui
            semantic = []

        # ======================================================
        # BUILD OUTPUT
        # ======================================================
        parts = []

        if summary:
            parts.append(f"🧠 Resumo:\n{summary}")

        if events:
            parts.append("📜 Eventos recentes:")
            parts.extend(f"- {e}" for e in events)

        if semantic:
            parts.append("🔎 Contexto relevante:")
            parts.extend(f"- {s}" for s in semantic)

        if not parts:
            return "📭 Nenhum contexto disponível."

        result = "\n\n".join(parts)

        # ======================================================
        # CACHE SET
        # ======================================================
        if self.cache:
            await self.cache.set(cache_key, result, ttl=30)

        return result
