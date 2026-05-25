from typing import Any

from fastapi import APIRouter, Depends

from semantic_context_server.interfaces.api.api_responder import ApiResponder
from semantic_context_server.interfaces.api.dependencies import get_container

router = APIRouter()


# ---------------------------------------------------------
# CREATE / START
# ---------------------------------------------------------
@router.post("/{campaign_id}")
async def create_campaign(
    campaign_id: str,
    container: Any = Depends(get_container),
) -> Any:
    responder = ApiResponder()

    created = await container.create_campaign.execute(campaign_id)

    if created:
        await responder.send(f"Campanha '{campaign_id}' criada.")
    else:
        await responder.send(f"Campanha '{campaign_id}' já existe.")

    return responder.response()


# ---------------------------------------------------------
# LIST
# ---------------------------------------------------------
@router.get("/")
async def list_campaigns(container: Any = Depends(get_container)) -> Any:
    responder = ApiResponder()

    campaigns = await container.list_campaigns.execute()

    if not campaigns:
        await responder.send("Nenhuma campanha encontrada.")
    else:
        await responder.send("Campanhas:\n" + "\n".join(f"- {c}" for c in campaigns))

    return responder.response()


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------
@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    container: Any = Depends(get_container),
) -> Any:
    responder = ApiResponder()

    ok = await container.delete_campaign.execute(campaign_id)

    if not ok:
        await responder.send("Campanha não encontrada.")
    else:
        await responder.send(f"Campanha '{campaign_id}' removida.")

    return responder.response()
