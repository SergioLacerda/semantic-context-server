import math
import time
from collections import defaultdict


class NarrativeGraph:
    """
    Knowledge Graph narrativo com:

    ✔ peso estrutural
    ✔ recência (decay temporal)
    ✔ suporte opcional a embeddings (híbrido)
    ✔ sem IO / sem dependência externa
    """

    def __init__(self) -> None:
        # { entity: { other: edge_data } }
        self._graph: dict[str, dict[str, dict]] = defaultdict(dict)

        # embeddings opcionais
        self._embeddings: dict[str, list[float]] = {}

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(
        self,
        *,
        entities: list[str],
        context: dict | None = None,
    ) -> None:
        if not entities:
            return

        now = time.time()
        context = context or {}

        for e in entities:
            for other in entities:
                if e == other:
                    continue

                edge = self._graph[e].get(other)

                if not edge:
                    self._graph[e][other] = {
                        "weight": 1.0,
                        "last_seen": now,
                        "contexts": [context],
                    }
                else:
                    edge["weight"] += 1.0
                    edge["last_seen"] = now

                    if len(edge["contexts"]) < 5:
                        edge["contexts"].append(context)

    # ==========================================================
    # EMBEDDINGS (opcional)
    # ==========================================================

    def set_embedding(self, entity: str, vector: list[float]) -> None:
        self._embeddings[entity] = vector

    def _cosine(self, a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b, strict=True))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    # ==========================================================
    # QUERY (HYBRID SCORING)
    # ==========================================================

    def related(
        self,
        entities: list[str],
        *,
        limit: int = 10,
        use_embeddings: bool = True,
        decay_lambda: float = 0.001,
    ) -> list[str]:
        scores: dict[str, float] = {}
        now = time.time()

        for e in entities:
            neighbors = self._graph.get(e, {})

            for other, data in neighbors.items():
                if other in entities:
                    continue

                structural = data["weight"]

                # 🔥 decay temporal exponencial
                age = now - data["last_seen"]
                temporal = math.exp(-decay_lambda * age)

                score = structural * temporal

                # 🔥 componente semântico (opcional)
                if use_embeddings:
                    emb_a = self._embeddings.get(e)
                    emb_b = self._embeddings.get(other)

                    if emb_a and emb_b:
                        sim = self._cosine(emb_a, emb_b)
                        score += 0.5 * sim  # peso semântico

                # 🔥 max pooling
                scores[other] = max(score, scores.get(other, 0.0))

        ranked = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return [entity for entity, _ in ranked[:limit]]

    # ==========================================================
    # MAINTENANCE
    # ==========================================================

    def prune(self, max_nodes: int = 1000) -> None:
        if len(self._graph) <= max_nodes:
            return

        sorted_nodes = sorted(
            self._graph.items(),
            key=lambda x: sum(edge["weight"] for edge in x[1].values()),
        )

        to_remove = len(self._graph) - max_nodes

        for i in range(to_remove):
            key = sorted_nodes[i][0]
            del self._graph[key]
            self._embeddings.pop(key, None)

    # ==========================================================
    # SERIALIZAÇÃO
    # ==========================================================

    def to_dict(self) -> dict:
        return {
            "graph": self._graph,
            "embeddings": self._embeddings,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NarrativeGraph":
        instance = cls()

        if not data:
            return instance

        instance._graph = defaultdict(dict, data.get("graph", {}))
        instance._embeddings = data.get("embeddings", {})

        return instance
