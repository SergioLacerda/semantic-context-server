from typing import Any

from packages.features.rpg_engine.domain.narrative.narrative_memory import NarrativeMemory


class ContextBuilder:
    def __init__(
        self,
        memory_service: Any,
        graph_service: Any = None,
        entity_extractor: Any = None,
        *,
        max_recent_events: int = 10,
    ) -> None:
        self.memory = memory_service
        self.graph = graph_service
        self.entity_extractor = entity_extractor
        self.max_recent_events = max_recent_events

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    async def build(
        self,
        *,
        campaign_id: str,
        action: str,
        intent: str = "DEFAULT",
    ) -> tuple[dict[str, Any], NarrativeMemory]:

        # ---------------------------------------------------------
        # 1. MEMORY
        # ---------------------------------------------------------
        try:
            memory = await self.memory.load_memory(campaign_id)

            if not hasattr(memory, "get_recent_events"):
                raise ValueError("invalid memory")

        except Exception:
            memory = NarrativeMemory()

        events = memory.get_recent_events(limit=50)
        summary = memory.get_summary()

        # ---------------------------------------------------------
        # 2. ENTITIES
        # ---------------------------------------------------------
        entities = [e.lower() for e in self._extract_entities(action)]

        # ---------------------------------------------------------
        # 3. GRAPH
        # ---------------------------------------------------------
        related_entities = await self._get_related_entities(
            campaign_id,
            entities,
        )

        # ---------------------------------------------------------
        # 4. RANK EVENTS
        # ---------------------------------------------------------
        ranked_events = self._rank_events(
            events,
            entities,
            related_entities,
        )

        recent_events = self._sanitize_list(ranked_events[: self.max_recent_events])

        # ---------------------------------------------------------
        # 5. FINAL CONTEXT
        # ---------------------------------------------------------
        ctx = {
            "summary": summary,
            "recent_events": recent_events,
            "retrieved": recent_events[:3],  # 🔥 RAG explícito
            "entities": entities,
            "related_entities": related_entities,
            "scene_type": intent,
            "intent": intent,
        }

        return ctx, memory

    # ==========================================================
    # INTERNAL
    # ==========================================================

    def _extract_entities(self, text: str) -> list[str]:
        if not self.entity_extractor:
            return []

        try:
            extracted = self.entity_extractor.extract(text)

            if not isinstance(extracted, list):
                return []

            return self._sanitize_list(extracted)

        except Exception:
            return []

    async def _get_related_entities(self, campaign_id: str, entities: list[str]) -> list[str]:
        if not self.graph or not entities:
            return []

        try:
            rel = await self.graph.related(
                campaign_id=campaign_id,
                entities=entities,
            )

            return self._dedupe(rel)

        except Exception:
            return []

    # ==========================================================
    # RANKING
    # ==========================================================

    def _rank_events(
        self, events: list[str], entities: list[str], related_entities: list[str]
    ) -> list[str]:
        if not events:
            return []

        events = events[:50]  # 🔥 proteção

        scored = []

        for idx, e in enumerate(events):
            if not isinstance(e, str):
                continue

            text = e.lower()
            score = 0.0

            for ent in entities:
                if ent in text:
                    score += 3

            for ent in related_entities:
                if ent.lower() in text:
                    score += 1

            # 🔥 recência real
            score += 1 / (idx + 1)

            scored.append((e, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [e for e, _ in scored]

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _sanitize_list(self, values: list[str]) -> list[str]:
        return [str(v).strip() for v in values if isinstance(v, str) and v.strip()]

    def _dedupe(self, values: list[str]) -> list[str]:
        seen = set()
        result = []

        for v in values:
            if not isinstance(v, str):
                continue

            key = v.strip().lower()
            if key and key not in seen:
                seen.add(key)
                result.append(v.strip())

        return result
