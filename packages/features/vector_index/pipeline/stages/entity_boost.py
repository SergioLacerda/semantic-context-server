from collections.abc import Iterable


class EntityProvider:
    """
    Interface esperada:
    - get_entities() -> set[str]
    """

    def get_entities(self) -> set[str]:
        raise NotImplementedError


class EntityBoost:
    """
    Aumenta score quando query e documento compartilham entidades.
    """

    def __init__(self, entity_provider: EntityProvider):
        self.entity_provider = entity_provider

    # ---------------------------------------------------------
    # score único
    # ---------------------------------------------------------

    def score(self, query_tokens: Iterable[str], doc_tokens: Iterable[str]) -> float:
        entities = self.entity_provider.get_entities()

        if not entities:
            return 0.0

        q = set(query_tokens)
        d = set(doc_tokens)

        overlap = q & d & entities

        if not overlap:
            return 0.0

        # normalização leve
        return min(1.0, len(overlap) * 0.5)

    # ---------------------------------------------------------
    # score batch
    # ---------------------------------------------------------

    def batch_score(
        self, query_tokens: Iterable[str], docs_tokens: list[Iterable[str]]
    ) -> list[float]:
        entities = self.entity_provider.get_entities()

        if not entities:
            return [0.0] * len(docs_tokens)

        q = set(query_tokens)

        scores = []

        for tokens in docs_tokens:
            d = set(tokens)

            overlap = q & d & entities

            if not overlap:
                scores.append(0.0)
            else:
                scores.append(min(1.0, len(overlap) * 0.5))

        return scores
