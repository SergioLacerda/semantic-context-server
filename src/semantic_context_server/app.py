from fastapi import FastAPI

from semantic_context_server.bootstrap.lifecycle import lifespan
from semantic_context_server.interfaces.api.middleware.request_context_middleware import (
    request_context_middleware,
)
from semantic_context_server.interfaces.api.routes.router import api_router
from semantic_context_server.shared.logging.config import setup_logging

setup_logging()


def create_app() -> FastAPI:
    app = FastAPI(
        title="RPG Narrative Server",
        lifespan=lifespan,
    )

    app.middleware("http")(request_context_middleware)

    app.include_router(api_router)

    return app


app = create_app()
