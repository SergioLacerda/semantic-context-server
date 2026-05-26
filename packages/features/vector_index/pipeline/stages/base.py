class BaseStage:
    priority = 50
    min_candidates = 0

    async def run(self, ctx: dict) -> dict:
        raise NotImplementedError
