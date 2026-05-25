import asyncio
from typing import Any


class HealthService:
    def __init__(self, container: Any) -> None:
        self.container = container

    # ---------------------------------------------------------
    # liveness (rápido, sem dependências)
    # ---------------------------------------------------------

    def is_alive(self) -> bool:
        return True

    # ---------------------------------------------------------
    # readiness (depende de infra)
    # ---------------------------------------------------------

    async def is_ready(self) -> bool:
        if self.container is None:
            return True
        try:
            vector_index = self.container.vector_index

            # se tiver método async/sync, trata ambos
            if hasattr(vector_index, "ensure_ann_ready"):
                maybe = vector_index.ensure_ann_ready()
                if asyncio.iscoroutine(maybe):
                    await maybe

            return True

        except Exception:
            return False

    # ---------------------------------------------------------
    # status completo (opcional)
    # ---------------------------------------------------------

    async def status(self) -> dict[str, Any]:
        ready = await self.is_ready()

        embedding = getattr(self.container, "embedding", None)
        storage = getattr(self.container, "storage", None)

        return {
            "status": "ready" if ready else "loading",
            "components": {
                "vector_index": "ok" if ready else "loading",
                "embedding": type(embedding).__name__ if embedding is not None else "unknown",
                "storage": type(storage).__name__ if storage is not None else "unknown",
            },
        }
