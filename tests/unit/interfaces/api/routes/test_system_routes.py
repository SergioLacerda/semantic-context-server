import pytest

from semantic_context_server.interfaces.api.routes.system_controller import get_config


@pytest.mark.asyncio
async def test_get_system_config(container):
    data = await get_config(container)
    assert "environment" in data
    assert "storage" in data
    assert "llm_provider" in data


def test_api_router_mounts():
    from packages.interfaces.http_api.router import api_router

    paths = {route.path for route in api_router.routes}
    assert "/health" in paths
    assert "/system/config" in paths
