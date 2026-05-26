from typing import Any


class RetrievalPipeline:
    def __init__(self, stages: list[Any]) -> None:
        self.stages = sorted(stages, key=lambda s: getattr(s, "priority", 50))

    def run(self, ctx: Any) -> list[Any]:
        candidates: list[Any] = []

        for stage in self.stages:
            if candidates and len(candidates) < getattr(stage, "min_candidates", 0):
                continue

            candidates = stage.run(ctx, candidates)

        return candidates
