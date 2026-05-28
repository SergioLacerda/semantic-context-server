"""HTTP interface package entrypoint.

Wave 2.13 package-native app bootstrap.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from packages.core.bootstrap_runtime import LifecycleOrchestrator
from packages.core.bootstrap_runtime.lifecycle import setup_signal_handlers
from packages.interfaces.http_api.assembler import NarrativeServerAssembler
from packages.interfaces.http_api.router import api_router
from packages.core.shared_kernel.logging_context import setup_logging
from semantic_context_server.application.runtime.app_runtime import AppRuntime
from semantic_context_server.shared.cache.cache import CacheManager
from semantic_context_server.interfaces.api.middleware.request_context_middleware import (
    request_context_middleware,
)

setup_logging()


@asynccontextmanager
async def orchestrated_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_signal_handlers()
    orchestrator = LifecycleOrchestrator(NarrativeServerAssembler())
    graph = await orchestrator.start()

    app.state.orchestrator = orchestrator
    app.state.service_graph = graph
    app.state.runtime = graph.resolve(AppRuntime) if graph.has(AppRuntime) else None
    app.state.container = app.state.runtime.container if app.state.runtime is not None else None
    app.state.cache_manager = graph.resolve(CacheManager) if graph.has(CacheManager) else None

    try:
        yield
    finally:
        await orchestrator.shutdown("app_shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title="RPG Narrative Server",
        lifespan=orchestrated_lifespan,
    )
    app.middleware("http")(request_context_middleware)
    app.include_router(api_router)
    return app


app = create_app()

__all__ = ["app", "create_app"]
