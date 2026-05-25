from typing import Any, Protocol


class RetrievalLike(Protocol):
    async def search(self, query: str) -> Any: ...
