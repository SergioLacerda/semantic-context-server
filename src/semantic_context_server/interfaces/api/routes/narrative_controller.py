from typing import Any

from fastapi import APIRouter, Depends

from semantic_context_server.interfaces.api.dependencies import get_narrative_usecase
from semantic_context_server.interfaces.api.schemas.narrative_schema import (
    NarrativeEventRequest,
)

router = APIRouter()


@router.post("/{campaign_id}/event")
async def narrative_event(
    campaign_id: str,
    payload: NarrativeEventRequest,
    usecase: Any = Depends(get_narrative_usecase),
) -> Any:
    response = await usecase.execute(
        campaign_id=campaign_id, action=payload.action, user_id=payload.user_id
    )

    return {
        "status": "ok",
        "response": response,
    }
