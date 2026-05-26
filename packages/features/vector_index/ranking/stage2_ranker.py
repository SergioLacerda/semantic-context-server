import contextlib
import heapq
from typing import Any


class Stage2Ranker:
    """
    Refinamento intermediário:
    - lexical
    - temporal
    - cluster proximity
    """

    def __init__(self, top_k: int = 60, executor: Any = None) -> None:
        self.top_k = top_k
        self.executor = executor

    async def rank(self, ctx: Any, candidates: list[str]) -> list[str]:
        if not candidates:
            return candidates

        query_tokens = set(getattr(ctx, "query_tokens", []) or [])

        get_tokens = getattr(ctx, "get_tokens", None)
        temporal = getattr(ctx, "temporal_index", None)
        ann = getattr(ctx, "ann", None)

        # Se tivermos muitos candidatos, despachamos o loop para o Executor
        executor = self.executor or getattr(ctx, "executor", None)
        if executor and len(candidates) > 20:
            result: list[str] = await executor.run(
                self._score_loop, ctx, candidates, query_tokens, get_tokens, temporal, ann
            )
            return result

        return self._score_loop(ctx, candidates, query_tokens, get_tokens, temporal, ann)

    def _score_loop(
        self,
        ctx: Any,
        candidates: list[str],
        query_tokens: set[str],
        get_tokens: Any,
        temporal: Any,
        ann: Any,
    ) -> list[str]:
        heap: list[tuple[float, str]] = []

        for doc_id in candidates:
            score = 0.0

            # -----------------------------------------------------
            # lexical
            # -----------------------------------------------------
            tokens = get_tokens(doc_id) if get_tokens else []
            tokens = set(tokens or [])

            score += 0.4 * len(query_tokens & tokens)

            # -----------------------------------------------------
            # temporal
            # -----------------------------------------------------
            if temporal:
                score += 0.3 * temporal.recency_score(doc_id)

            # -----------------------------------------------------
            # cluster
            # -----------------------------------------------------
            if ann and hasattr(ann, "cluster_similarity"):
                with contextlib.suppress(Exception):
                    score += 0.3 * ann.cluster_similarity(ctx.q_vec, doc_id)

            item = (score, doc_id)

            if len(heap) < self.top_k:
                heapq.heappush(heap, item)
            else:
                heapq.heappushpop(heap, item)

        heap.sort(reverse=True)

        return [doc_id for _, doc_id in heap]
