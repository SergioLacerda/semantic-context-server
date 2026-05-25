from collections import defaultdict
from typing import Any

from semantic_context_server.infrastructure.nlp.entity_extractor import EntityExtractor

entity_extractor = EntityExtractor()


class NarrativeGraph:
    def __init__(self, repository: Any, campaign_id: str) -> None:
        self.repository = repository
        self.campaign_id = campaign_id

        self.graph: dict[str, Any] = {}
        self.frequency: defaultdict[str, int] = defaultdict(int)

    # ---------------------------------------------------------
    # lifecycle
    # ---------------------------------------------------------

    async def load(self) -> None:
        data = await self.repository.load(self.campaign_id)

        self.graph = data.get("graph", {})
        self.frequency = defaultdict(int, data.get("frequency", {}))

    async def persist(self) -> None:
        await self.repository.save(
            self.campaign_id,
            {
                "graph": self.graph,
                "frequency": dict(self.frequency),
            },
        )

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    async def update_from_event(self, text: str) -> None:
        entities = entity_extractor.extract(text)

        for e in entities:
            self.frequency[e] += 1

            node = self.graph.setdefault(
                e,
                {
                    "links": set(),
                },
            )

            for other in entities:
                if other == e:
                    continue

                node["links"].add(other)

        await self.persist()

    # ---------------------------------------------------------
    # QUERY EXPANSION
    # ---------------------------------------------------------

    def related(self, query: str) -> set:
        entities = entity_extractor.extract(query)

        related = set()

        for e in entities:
            node = self.graph.get(e)
            if node:
                related.update(node["links"])

        return related

    # ---------------------------------------------------------
    # 🔥 DECISION ENGINE (CORE)
    # ---------------------------------------------------------

    def decide_focus(self, query: str, top_k: int = 5) -> list:
        """
        Retorna entidades mais relevantes para a narrativa atual
        """

        entities = entity_extractor.extract(query)

        scores: defaultdict[str, float] = defaultdict(float)

        for e in entities:
            # peso base
            scores[e] += 1.0

            # frequência histórica
            scores[e] += self.frequency.get(e, 0) * 0.2

            # centralidade (número de conexões)
            node = self.graph.get(e)
            if node:
                scores[e] += len(node["links"]) * 0.1

                # influência indireta (vizinhos)
                for neighbor in node["links"]:
                    scores[neighbor] += 0.3

        # ordena
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return [e for e, _ in ranked[:top_k]]

    # ---------------------------------------------------------
    # 🔥 CONTEXT BOOST
    # ---------------------------------------------------------

    def score_document(self, query: str, text: str) -> float:
        """
        Score narrativo para ranking de contexto
        """

        focus_entities = self.decide_focus(query)

        text_lower = text.lower()

        score = 0.0

        for e in focus_entities:
            if e.lower() in text_lower:
                score += 0.2

        return min(score, 1.0)

    # ---------------------------------------------------------
    # 🔥 DECISION HINT (LLM)
    # ---------------------------------------------------------

    def build_narrative_hint(self, query: str) -> str:
        """
        Gera instruções narrativas para o LLM
        """

        focus = self.decide_focus(query)

        if not focus:
            return ""

        return f"""
Foco narrativo atual:
{", ".join(focus)}

Priorize estes elementos na narrativa.
""".strip()
