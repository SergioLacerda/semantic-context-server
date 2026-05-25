import asyncio
from typing import Any


class ContextService:
    def __init__(
        self,
        vector_reader_campaign: Any,
        vector_reader_world: Any = None,
        embedding_cache: Any = None,
        narrative_graph: Any = None,
    ) -> None:
        self.campaign_reader = vector_reader_campaign
        self.world_reader = vector_reader_world
        self.embedding_cache = embedding_cache
        self.graph = narrative_graph

    # ==========================================================
    # MAIN API
    # ==========================================================

    async def search(
        self,
        campaign_id: str,
        query: str,
        k: int = 4,
        intent: str | None = None,
    ) -> list[str]:

        expanded_query = await self._expand_query(query)

        campaign_docs, world_docs = await asyncio.gather(
            self._safe_search(self.campaign_reader, campaign_id, expanded_query, k * 3),
            self._safe_search(self.world_reader, campaign_id, expanded_query, k * 3),
        )

        ranked = await self._rank(
            query,
            campaign_docs,
            world_docs,
            intent,
            k,
        )

        return [d["text"] for d in ranked if d.get("text")]

    # ==========================================================
    # QUERY EXPANSION
    # ==========================================================

    async def _expand_query(self, query: str) -> str:
        if not self.graph:
            return query

        try:
            related = await self.graph.related(query)
        except Exception:
            return query

        if not related:
            return query

        expansion = " ".join(list(related)[:3])
        return f"{query} {expansion}"

    # ==========================================================

    async def _safe_search(self, reader: Any, campaign_id: str, query: str, k: int) -> list[Any]:
        if not reader:
            return []

        try:
            result: list[Any] = await reader.search(
                campaign_id=campaign_id,
                query=query,
                k=k,
            )
            return result
        except Exception:
            return []

    # ==========================================================

    async def _rank(
        self,
        query: str,
        campaign_docs: list[Any],
        world_docs: list[Any],
        intent: str | None,
        k: int,
    ) -> list[Any]:
        if not self.embedding_cache:
            return (campaign_docs + world_docs)[:k]

        weights = self._resolve_weights(intent)

        for d in campaign_docs:
            d["_source"] = "campaign"
        for d in world_docs:
            d["_source"] = "world"

        all_docs = campaign_docs + world_docs
        texts = [d["text"] for d in all_docs if d.get("text")]

        try:
            embeddings = await self.embedding_cache.get_many(texts + [query])
            doc_embeddings = embeddings[:-1]
            query_emb = embeddings[-1]
        except Exception:
            doc_embeddings = [None] * len(texts)
            query_emb = None

        scored = []

        for doc, emb in zip(all_docs, doc_embeddings, strict=False):
            base_score = self._cosine(query_emb, emb) if emb else 0

            try:
                narrative_boost = (
                    self.graph.score_document(query, doc["text"])
                    if self.graph and hasattr(self.graph, "score_document")
                    else 0
                )
            except Exception:
                narrative_boost = 0

            weight = weights.get(doc["_source"], 1.0)

            final_score = (base_score * weight) + (narrative_boost * 0.3)

            scored.append(
                {
                    "doc": doc,
                    "score": final_score,
                    "embedding": emb,
                }
            )

        scored.sort(key=lambda x: x["score"], reverse=True)

        candidates = scored[: k * 2]
        scored = self._deduplicate(candidates)
        scored = self._diversify(scored)
        scored = self._balance_sources(scored, k)

        scored = self._fill_to_k(scored, candidates, k)

        return [s["doc"] for s in scored[:k]]

    # ==========================================================

    def _fill_to_k(self, scored: list[Any], candidates: list[Any], k: int) -> list[Any]:
        if len(scored) >= k:
            return scored
        seen_ids = {id(item["doc"]) for item in scored}
        for item in candidates:
            if len(scored) >= k:
                break
            if id(item["doc"]) not in seen_ids:
                scored.append(item)
                seen_ids.add(id(item["doc"]))
        return scored

    def _resolve_weights(self, intent: str | None) -> dict[str, float]:
        base = {"campaign": 1.0, "world": 0.6}

        mapping = {
            "ACTION": {"campaign": 1.0, "world": 0.4},
            "ROLL": {"campaign": 0.9, "world": 0.2},
            "LORE": {"campaign": 0.7, "world": 1.0},
        }

        return mapping.get(intent or "", base)

    # ==========================================================

    def _deduplicate(
        self, scored: list[dict[str, Any]], threshold: float = 0.92
    ) -> list[dict[str, Any]]:
        result = []

        for item in scored:
            emb = item["embedding"]

            if not emb:
                result.append(item)
                continue

            source = item["doc"].get("_source")
            if any(
                self._cosine(emb, r["embedding"]) > threshold and source == r["doc"].get("_source")
                for r in result
                if r["embedding"]
            ):
                continue

            result.append(item)

        return result

    # ==========================================================

    def _diversify(
        self, scored: list[dict[str, Any]], lambda_param: float = 0.7
    ) -> list[dict[str, Any]]:
        if not scored:
            return []

        selected = [scored[0]]

        for candidate in scored[1:]:
            sims = [
                self._cosine(candidate["embedding"], s["embedding"])
                for s in selected
                if candidate["embedding"] and s["embedding"]
            ]

            max_sim = max(sims) if sims else 0

            candidate["score"] = lambda_param * candidate["score"] - (1 - lambda_param) * max_sim

            selected.append(candidate)

        selected.sort(key=lambda x: x["score"], reverse=True)
        return selected

    # ==========================================================

    def _balance_sources(self, scored: list[dict[str, Any]], k: int) -> list[dict[str, Any]]:
        if len(scored) <= 1 or k <= 1:
            return scored

        source_to_items: dict[str, list[dict[str, Any]]] = {}
        for item in scored:
            source = item["doc"].get("_source")
            source_to_items.setdefault(source, []).append(item)

        # If all results come from one source, keep original order.
        if len([s for s in source_to_items if s]) < 2:
            return scored

        ordered_sources = sorted(
            source_to_items.keys(), key=lambda s: source_to_items[s][0]["score"], reverse=True
        )
        balanced: list[dict[str, Any]] = []

        while len(balanced) < len(scored):
            progressed = False
            for source in ordered_sources:
                if not source_to_items[source]:
                    continue
                balanced.append(source_to_items[source].pop(0))
                progressed = True
                if len(balanced) >= len(scored):
                    break
            if not progressed:
                break

        return balanced

    # ==========================================================

    def _cosine(self, a: list[float] | None, b: list[float] | None) -> float:
        if not a or not b:
            return 0

        dot = sum(x * y for x, y in zip(a, b, strict=True))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0

        return float(dot / (norm_a * norm_b))
