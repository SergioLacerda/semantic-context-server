class DummyIndex:
    def __init__(self, result=None):
        self.result = result
        self.calls: list[dict] = []
        self.embedding_service = DummyEmbeddingService()

    async def search(self, query, q_vec, k):
        self.calls.append(
            {
                "query": query,
                "q_vec": q_vec,
                "k": k,
            }
        )

        if self.result is not None:
            return self.result

        return [f"result:{query}:{k}"]


class DummyEmbeddingCache:
    def __init__(self, result=None):
        self.result = result or [1, 2, 3]
        self.calls: list[str] = []

    async def get(self, query):
        self.calls.append(query)
        return self.result


class DummySemanticCache:
    def __init__(self):
        self.data = {}
        self.get_calls: list[dict] = []
        self.set_calls: list[dict] = []

    def get(self, query, q_vec):
        self.get_calls.append({"query": query, "q_vec": q_vec})
        return self.data.get(query)

    async def set(self, query, q_vec, result):
        self.set_calls.append(
            {
                "query": query,
                "q_vec": q_vec,
                "result": result,
            }
        )
        self.data[query] = result


class DummyEmbeddingService:
    def embed(self, query):
        return [1, 2, 3]
