import random
from typing import Any


class CandidateSetReservoir:
    priority = 50

    def __init__(self, max_size: int = 100) -> None:
        self.max_size = max_size

    async def run(self, ctx: Any) -> Any:
        if not ctx.candidates:
            return ctx

        if len(ctx.candidates) > self.max_size:
            ctx.candidates = random.sample(ctx.candidates, self.max_size)

        return ctx
