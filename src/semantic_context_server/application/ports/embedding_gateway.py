import asyncio
from collections.abc import Iterable
from typing import Protocol, runtime_checkable


@runtime_checkable
class EmbeddingGateway(Protocol):
    @property
    def dimension(self) -> int | None: ...

    @property
    def supports_batch(self) -> bool: ...

    async def embed(self, text: str) -> list[float]: ...

    async def embed_batch(
        self,
        texts: Iterable[str],
        *,
        concurrency: int = 5,
    ) -> list[list[float]]:
        texts_list = list(texts)

        if not texts_list:
            return []

        if concurrency <= 1:
            return [await self.embed(t) for t in texts_list]

        semaphore = asyncio.Semaphore(concurrency)

        async def _embed_one(text: str) -> list[float]:
            async with semaphore:
                return await self.embed(text)

        tasks = [_embed_one(t) for t in texts_list]

        return await asyncio.gather(*tasks)
