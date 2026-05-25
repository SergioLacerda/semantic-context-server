# vector_index/api/index.py
from typing import Any


class VectorIndexAPI:
    def __init__(self, engine: Any) -> None:
        self._engine = engine

    async def search(self, query: str, k: int = 4) -> Any:
        return await self._engine.search(query, k)
