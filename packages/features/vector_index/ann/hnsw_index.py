import random
from collections import defaultdict
from typing import Any

from packages.features.vector_index.utils.similarity import cosine_similarity


class HNSWIndex:
    def __init__(self, docs: list[dict[str, Any]], M: int = 6, ef: int = 20) -> None:
        self.M = M  # número de vizinhos
        self.ef = ef  # largura da busca

        self.docs = docs
        self.layers: list[list[dict[str, Any]]] = []
        self.graph: dict[Any, list[dict[str, Any]]] = defaultdict(list)

        self.entry_point: dict[str, Any] | None = None

        self._build()

    # ---------------------------------------------------------
    # construção
    # ---------------------------------------------------------

    def _random_level(self) -> int:
        level = 0
        while random.random() < 0.5:
            level += 1
        return level

    def _build(self) -> None:
        for doc in self.docs:
            level = self._random_level()

            while len(self.layers) <= level:
                self.layers.append([])

            for layer_idx in range(level + 1):
                self.layers[layer_idx].append(doc)

            if self.entry_point is None:
                self.entry_point = doc
                continue

            neighbors = self._search_layer(doc["vector"], self.entry_point)

            for n in neighbors[: self.M]:
                self.graph[doc["id"]].append(n)
                self.graph[id(n)].append(doc)

    # ---------------------------------------------------------
    # busca em camada
    # ---------------------------------------------------------

    def _search_layer(self, q_vec: list[float], entry: dict[str, Any]) -> list[dict[str, Any]]:
        visited: set[int] = set()
        candidates: list[dict[str, Any]] = [entry]
        best: list[dict[str, Any]] = [entry]

        while candidates:
            current = candidates.pop()

            for neighbor in self.graph[id(current)]:
                if id(neighbor) in visited:
                    continue

                visited.add(id(neighbor))

                score = cosine_similarity(q_vec, neighbor["vector"])

                if len(best) < self.ef or score > cosine_similarity(q_vec, best[-1]["vector"]):
                    best.append(neighbor)
                    best.sort(
                        key=lambda d: cosine_similarity(q_vec, d["vector"]),
                        reverse=True,
                    )

                    if len(best) > self.ef:
                        best.pop()

                    candidates.append(neighbor)

        return best

    # ---------------------------------------------------------
    # busca principal
    # ---------------------------------------------------------

    def search(self, q_vec: list[float], k: int = 20) -> list[dict[str, Any]]:
        if not self.entry_point:
            return []

        entry = self.entry_point

        for _layer in reversed(self.layers):
            best = self._search_layer(q_vec, entry)

            if best:
                entry = best[0]

        result = self._search_layer(q_vec, entry)

        return result[:k]
