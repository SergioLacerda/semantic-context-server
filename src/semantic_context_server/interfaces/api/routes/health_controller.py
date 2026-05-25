from typing import Any

from fastapi import APIRouter, Depends

from semantic_context_server.interfaces.api.dependencies import get_health_service

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready(health_service: Any = Depends(get_health_service)) -> Any:
    is_ready = True

    if hasattr(health_service, "is_ready"):
        is_ready = await health_service.is_ready()

    return {"status": "ready" if is_ready else "loading"}
