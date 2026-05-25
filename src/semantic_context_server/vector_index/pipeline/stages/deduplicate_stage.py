from typing import Any


class DeduplicateStage:
    priority = 75

    async def run(self, ctx: Any) -> Any:
        if not ctx.candidates:
            return ctx

        seen: set[Any] = set()
        unique: list[Any] = []

        for doc_id in ctx.candidates:
            if doc_id not in seen:
                seen.add(doc_id)
                unique.append(doc_id)

        ctx.candidates = unique

        return ctx
