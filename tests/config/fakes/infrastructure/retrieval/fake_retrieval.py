class FakeContextWindow:
    def __init__(self, vector_index=None):
        self.vector_index = vector_index
        self.called_with = None

    async def search(self, query, k=4):
        self.called_with = (query, k)

        if self.vector_index:
            result = await self.vector_index.search_async(query, k)
            return [r["text"] for r in result]

        return []
