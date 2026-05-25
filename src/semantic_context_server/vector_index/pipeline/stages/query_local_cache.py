from typing import Any


class QueryLocalCache:
    priority = 30

    def __init__(self) -> None:
        self.cache: dict[str, list[Any]] = {}

    async def run(self, ctx: Any) -> Any:
        key = ctx.query

        if key in self.cache:
            ctx.candidates = self.cache[key]
            ctx._cache_hit = True
            return ctx

        ctx._cache_hit = False
        return ctx

    def save(self, query: str, candidates: list[Any]) -> None:
        self.cache[query] = candidates
