import asyncio
from typing import Any

from semantic_context_server.vector_index.utils.similarity import cosine_similarity


class RankingFinal:
    def __init__(
        self,
        contextual_score: Any = None,
        entity_boost: Any = None,
        weight_base: float = 1.0,
        weight_context: float = 0.3,
        executor: Any = None,
        weight_entity: float = 0.5,
        top_k: int = 4,
    ) -> None:
        self.contextual_score = contextual_score
        self.entity_boost = entity_boost

        self.weight_base = weight_base
        self.weight_context = weight_context
        self.weight_entity = weight_entity
        self.executor = executor
        self.top_k = top_k

    async def rank(self, ctx: Any, candidates: list[str]) -> list[str]:
        if not candidates:
            return []

        # 1. Busca vetores em paralelo (Async I/O)
        reader = getattr(ctx, "vector_reader", None)
        tasks = [reader.get(doc_id) for doc_id in candidates] if reader else []
        vectors = await asyncio.gather(*tasks)
        base_vectors = dict(zip(candidates, vectors, strict=False))

        query_tokens = set(getattr(ctx, "query_tokens", []) or [])

        get_tokens = getattr(ctx, "get_tokens", None)

        docs_tokens = [get_tokens(doc_id) if get_tokens else [] for doc_id in candidates]

        # 2. Delega o cálculo pesado de pesos para o Executor (CPU-bound)
        # Isso evita travar o event loop com loops de lógica/matemática
        executor = self.executor or getattr(ctx, "executor", None)
        if executor:
            result: list[str] = await executor.run(
                self._compute_final_scores,
                candidates,
                base_vectors,
                ctx.q_vec,
                query_tokens,
                docs_tokens,
            )
            return result

        return self._compute_final_scores(
            candidates, base_vectors, ctx.q_vec, query_tokens, docs_tokens
        )

    def _compute_final_scores(
        self,
        candidates: list[str],
        base_vectors: dict[str, Any],
        q_vec: Any,
        query_tokens: set[str],
        docs_tokens: list[Any],
    ) -> list[str]:
        """Lógica síncrona de pesos."""
        context_scores = (
            self.contextual_score.batch_score(docs_tokens)
            if self.contextual_score
            else [0.0] * len(candidates)
        )

        entity_scores = (
            self.entity_boost.batch_score(query_tokens, docs_tokens)
            if self.entity_boost
            else [0.0] * len(candidates)
        )

        results: list[tuple[float, str]] = []

        for i, doc_id in enumerate(candidates):
            vec = base_vectors.get(doc_id)
            base_sim = cosine_similarity(q_vec, vec) if vec else 0.0

            final_score = (
                self.weight_base * base_sim
                + self.weight_context * context_scores[i]
                + self.weight_entity * entity_scores[i]
            )

            results.append((final_score, doc_id))

        results.sort(reverse=True)

        return [doc_id for _, doc_id in results[: self.top_k]]
