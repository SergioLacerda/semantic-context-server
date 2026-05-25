from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from semantic_context_server.application.commands.roll.command import RollCommand
from semantic_context_server.application.contracts.response import Response

router = APIRouter(prefix="/dice", tags=["dice"])


# ==========================================================
# REQUEST DTO
# ==========================================================


class RollRequest(BaseModel):
    expression: str = Field(..., description="Dice expression (ex: 1d20, 2d6+3)")
    user_id: int = Field(..., description="User ID")


# ==========================================================
# DEPENDENCY (Campaign Resolver)
# ==========================================================


async def _campaign() -> Any:
    """
    🔥 Deve ser sobrescrito via dependency override nos testes
    ou implementado via container real (ex: CampaignScopedContainer)
    """
    raise NotImplementedError("Campaign dependency not configured")


# ==========================================================
# CONTROLLER
# ==========================================================


@router.post("/roll")
async def roll_dice(
    payload: RollRequest,
    campaign: Any = Depends(_campaign),
) -> Any:
    """
    🎲 Rola dados usando CQRS + UseCase

    Fluxo:
    API → Command → CommandBus → Handler → UseCase → Domain
    """
    try:
        command = RollCommand(
            expression=payload.expression,
            user_id=payload.user_id,
            campaign_id=campaign.campaign_id,
        )

        result: Response = await campaign.command_bus.execute(command)

        return {
            "text": result.text,
            "type": result.type,
            "metadata": result.metadata,
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "text": "Erro ao rolar os dados.",
                "type": "error",
                "metadata": {"error": "internal_error"},
            },
        ) from None
