from __future__ import annotations

import asyncio
from collections.abc import Iterable
from typing import Protocol, runtime_checkable


@runtime_checkable
class EmbeddingProviderContract(Protocol):
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
        semaphore = asyncio.Semaphore(concurrency)

        async def _embed_one(text: str) -> list[float]:
            async with semaphore:
                return await self.embed(text)

        return list(await asyncio.gather(*(_embed_one(t) for t in texts_list)))


@runtime_checkable
class EmbeddingGatewayContract(Protocol):
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
        semaphore = asyncio.Semaphore(concurrency)

        async def _embed_one(text: str) -> list[float]:
            async with semaphore:
                return await self.embed(text)

        return list(await asyncio.gather(*(_embed_one(t) for t in texts_list)))
