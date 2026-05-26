from typing import Any


class RetrievalAdapter:
    def __init__(self, engine: Any) -> None:
        self.engine = engine

    async def search(self, query: str) -> Any:
        return await self.engine.search(query)
