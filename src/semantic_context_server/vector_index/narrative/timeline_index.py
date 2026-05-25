import time
from collections import defaultdict


class TimelineIndex:
    """
    Index temporal simples para eventos narrativos.

    Permite:
    - score de recência
    - cadeia temporal (antes/depois)
    """

    def __init__(self) -> None:
        self.events: dict[str, float] = {}  # doc_id -> timestamp
        self.timeline: dict[float, list[str]] = defaultdict(list)  # timestamp -> [doc_ids]

    # ---------------------------------------------------------
    # indexação
    # ---------------------------------------------------------

    def add(self, doc_id: str, timestamp: float | None = None) -> None:
        ts = timestamp or time.time()

        self.events[doc_id] = ts
        self.timeline[ts].append(doc_id)

    # ---------------------------------------------------------
    # score de recência
    # ---------------------------------------------------------

    def recency_score(self, doc_id: str) -> float:
        ts = self.events.get(doc_id)

        if not ts:
            return 0.0

        now = time.time()

        # decaimento exponencial simples
        delta = now - ts

        return float(1.0 / (1.0 + delta / 3600))  # ~1h escala

    # ---------------------------------------------------------
    # cadeia temporal
    # ---------------------------------------------------------

    def causal_chain(self, doc_id: str, depth: int = 2) -> list[str]:
        if doc_id not in self.events:
            return []

        ts = self.events[doc_id]

        sorted_ts = sorted(self.timeline.keys())

        idx = sorted_ts.index(ts)

        results: list[str] = []

        # pegar vizinhos no tempo
        for i in range(1, depth + 1):
            if idx - i >= 0:
                results.extend(self.timeline[sorted_ts[idx - i]])

            if idx + i < len(sorted_ts):
                results.extend(self.timeline[sorted_ts[idx + i]])

        return results
