from typing import Any


class HybridRanker:
    def __init__(self, k: int = 60) -> None:
        self.k = k

    def fuse(
        self,
        *rank_lists: list[Any],
        weights: list[float] | None = None,
    ) -> list[Any]:
        if not rank_lists:
            return []

        weights = weights or [1.0] * len(rank_lists)

        scores: dict[Any, float] = {}

        for weight, rank_list in zip(weights, rank_lists, strict=False):
            if not rank_list:
                continue

            for i, doc in enumerate(rank_list):
                doc_id = doc["id"] if isinstance(doc, dict) else doc

                score = weight * (1 / (self.k + i))

                scores[doc_id] = scores.get(doc_id, 0) + score

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return [doc_id for doc_id, _ in ranked]
