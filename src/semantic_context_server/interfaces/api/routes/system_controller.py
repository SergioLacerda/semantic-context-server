from typing import Any

from fastapi import APIRouter, Depends

from semantic_context_server.interfaces.api.dependencies import get_container

router = APIRouter()


@router.get("/system/config")
async def get_config(container: Any = Depends(get_container)) -> Any:
    settings = container.settings

    return {
        # runtime
        "environment": settings.runtime.environment,
        "profile": settings.runtime.profile,
        # storage
        "storage": settings.app.storage,
        # llm
        "llm_provider": settings.llm.provider,
        "llm_model": settings.llm.model,
        # embeddings
        "embedding_provider": settings.embeddings.provider,
        "embedding_model": settings.embeddings.model,
        "embedding_dim": settings.embeddings.dimension,
    }
