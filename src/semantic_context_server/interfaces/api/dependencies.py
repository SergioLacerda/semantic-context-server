from typing import Any

from fastapi import Depends, Request

from packages.features.llm_gateway.contracts import LLMGatewayContract
from semantic_context_server.application.ports.event_bus import EventBus
from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.runtime.app_runtime import AppRuntime
from semantic_context_server.application.runtime.campaign_runtime import CampaignRuntime

# ==========================================================
# ROOT RUNTIME (FastAPI Depends chain)
# ==========================================================


def get_runtime(request: Request) -> AppRuntime:
    result: AppRuntime = request.app.state.runtime
    return result


# ==========================================================
# CONTAINER — reads from request.state (middleware-populated)
# ==========================================================


def get_container(request: Request) -> Any:
    """Return the DI container from request state or app state."""
    try:
        container = getattr(request.state, "container", None)
    except AttributeError:
        container = None
    if container is None:
        try:
            runtime = getattr(getattr(request.app, "state", None), "runtime", None)
            container = getattr(runtime, "container", None)
        except AttributeError:
            container = None
    return container


# ==========================================================
# GLOBAL DEPENDENCIES
# ==========================================================


async def get_event_bus(request: Request) -> Any:
    container = get_container(request)
    if container is None:
        return None
    bus = getattr(container, "event_bus", None)
    if bus is not None:
        return bus
    try:
        return container.resolve(EventBus)
    except Exception:
        return None


async def get_executor(request: Request) -> Any:
    container = get_container(request)
    if container is None:
        return None
    try:
        return container.resolve(ExecutorPort)
    except Exception:
        return None


async def get_llm(request: Request) -> Any:
    container = get_container(request)
    if container is None:
        return None
    try:
        return container.resolve(LLMGatewayContract)
    except Exception:
        return None


# ==========================================================
# HEALTH
# ==========================================================


async def get_health_service(request: Request) -> Any:
    from semantic_context_server.application.services.health_service import HealthService

    container = get_container(request)
    health = getattr(container, "health", None)
    if health is not None:
        return health
    return HealthService(container)


# ==========================================================
# CAMPAIGN RUNTIME
# ==========================================================


async def get_campaign_runtime(request: Request) -> CampaignRuntime:
    container = get_container(request)
    campaign_id = getattr(request.state, "campaign_id", None)
    result: CampaignRuntime = await container.campaigns.get(campaign_id)
    return result


async def get_narrative_usecase(request: Request) -> Any:
    container = get_container(request)
    campaign_id = getattr(request.state, "campaign_id", None)
    campaign = await container.campaigns.get(campaign_id)
    return campaign.narrative


async def get_roll_dice_usecase(request: Request) -> Any:
    container = get_container(request)
    campaign_id = getattr(request.state, "campaign_id", None)
    campaign = await container.campaigns.get(campaign_id)
    return campaign.roll_dice


async def get_end_session_usecase(request: Request) -> Any:
    container = get_container(request)
    campaign_id = getattr(request.state, "campaign_id", None)
    campaign = await container.campaigns.get(campaign_id)
    return campaign.end_session


# ==========================================================
# CAMPAIGN-SCOPED SERVICES (Depends chain compat)
# ==========================================================


async def get_campaign_runtime_depends(
    campaign_id: str,
    runtime: AppRuntime = Depends(get_runtime),
) -> CampaignRuntime:
    result: CampaignRuntime = await runtime.campaigns.get(campaign_id)
    return result


def get_memory_service(
    campaign: CampaignRuntime = Depends(get_campaign_runtime_depends),
) -> Any:
    return campaign.memory


def get_vector_reader(
    campaign: CampaignRuntime = Depends(get_campaign_runtime_depends),
) -> Any:
    return campaign.get("vector_reader")


def get_vector_writer(
    campaign: CampaignRuntime = Depends(get_campaign_runtime_depends),
) -> Any:
    return campaign.get("vector_writer")


# ==========================================================
# COMMAND BUS
# ==========================================================


async def get_command_bus(
    campaign_id: str,
    runtime: AppRuntime = Depends(get_runtime),
) -> Any:
    campaign = await runtime.campaigns.get(campaign_id)
    return campaign.command_bus
