class FakeVectorReader:
    def __init__(self, results: list[dict] = None):
        self.results = results or []
        self.called_with = None

    async def search(self, campaign_id: str, query: str, k: int) -> list[dict]:
        self.called_with = (campaign_id, query, k)
        return self.results


class FakeEmbeddingCache:
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    async def get_many(self, texts: list[str]) -> list[list[float]]:
        # Retorna vetores unitários simples para cálculo de cosseno
        return [[0.1] * self.dimension for _ in texts]


class FakeNarrativeGraph:
    def __init__(self, related_entities: list[str] = None):
        self.related_entities = set(related_entities or [])
        self.related_called_with = None
        self.score_called_with = []

    async def related(self, query: str) -> set[str]:
        self.related_called_with = query
        return self.related_entities

    def score_document(self, query: str, text: str) -> float:
        self.score_called_with.append((query, text))
        return 0.5 if any(q in text for q in query.split()) else 0.0
