import heapq
from typing import Any


class TopK:
    """
    Mantém os top-k elementos baseado em score.
    """

    def __init__(self, k: int):
        if k <= 0:
            raise ValueError("k must be > 0")

        self.k = k
        self._heap: list[tuple[float, Any]] = []

    # ---------------------------------------------------------
    # inserir item
    # ---------------------------------------------------------

    def push(self, score: float, item: Any) -> None:
        if len(self._heap) < self.k:
            heapq.heappush(self._heap, (score, item))
        else:
            heapq.heappushpop(self._heap, (score, item))

    # ---------------------------------------------------------
    # retornar resultados ordenados
    # ---------------------------------------------------------

    def results(self) -> list[Any]:
        return [item for _, item in sorted(self._heap, reverse=True)]

    # ---------------------------------------------------------
    # retornar com score (debug útil)
    # ---------------------------------------------------------

    def results_with_scores(self) -> list[tuple[float, Any]]:
        return sorted(self._heap, reverse=True)

    # ---------------------------------------------------------
    # limpar
    # ---------------------------------------------------------

    def clear(self) -> None:
        self._heap.clear()

    # ---------------------------------------------------------
    # tamanho atual
    # ---------------------------------------------------------

    def __len__(self) -> int:
        return len(self._heap)
