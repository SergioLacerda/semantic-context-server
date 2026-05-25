import signal
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.runtime.app_runtime import AppRuntime
from semantic_context_server.application.services.external_model_delegate import (
    ExternalModelDelegate,
)
from semantic_context_server.application.services.local_model_delegate import LocalModelDelegate
from semantic_context_server.application.usecases.prompt_service import PromptService
from semantic_context_server.bootstrap.container_builder import ContainerBuilder
from semantic_context_server.config.loader import load_settings
from semantic_context_server.shared.cache.cache import CacheManager


def _setup_signal_handlers() -> None:
    signal.signal(signal.SIGCHLD, signal.SIG_DFL)
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_IGN)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    builder = ContainerBuilder()
    container, campaign_manager = builder.build_tuple()

    # Cache manager (singleton)
    cache_manager = CacheManager()
    app.state.cache_manager = cache_manager

    # Model delegate selection based on settings
    settings = load_settings()
    model_delegate: ExternalModelDelegate | LocalModelDelegate
    if settings.model.delegate == "external":
        model_delegate = ExternalModelDelegate(settings)
    else:
        model_delegate = LocalModelDelegate(settings)

    # Prompt service exposing generate method
    app.state.prompt_service = PromptService(model_delegate, cache_manager)

    app.state.runtime = AppRuntime(container, campaign_manager)

    yield

    # shutdown ordered
    await app.state.runtime.shutdown()

    executor: ExecutorPort = container.resolve(ExecutorPort)
    await executor.shutdown()
