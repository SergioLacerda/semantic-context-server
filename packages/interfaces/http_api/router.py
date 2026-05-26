"""HTTP API router composition owned by package transport boundary."""

from fastapi import APIRouter

from semantic_context_server.interfaces.api.routes.benchmark_controller import (
    router as benchmark_router,
)
from semantic_context_server.interfaces.api.routes.campaign_controller import (
    router as campaign_router,
)
from semantic_context_server.interfaces.api.routes.dice_controller import (
    router as dice_router,
)
from semantic_context_server.interfaces.api.routes.health_controller import (
    router as health_router,
)
from semantic_context_server.interfaces.api.routes.narrative_controller import (
    router as narrative_router,
)
from semantic_context_server.interfaces.api.routes.system_controller import (
    router as system_router,
)

api_router = APIRouter()

api_router.include_router(
    narrative_router,
    prefix="/campaign",
    tags=["Narrative"],
)

api_router.include_router(
    campaign_router,
    prefix="/campaigns",
    tags=["Campaign"],
)

api_router.include_router(
    dice_router,
    prefix="/dice",
    tags=["Dice"],
)

api_router.include_router(
    health_router,
    tags=["Health"],
)

api_router.include_router(
    system_router,
    tags=["System"],
)

api_router.include_router(
    benchmark_router,
    tags=["Benchmark"],
)

__all__ = ["api_router"]
