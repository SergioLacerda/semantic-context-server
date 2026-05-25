import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def async_client(app):
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.mark.asyncio
async def test_get_system_config(async_client):
    async with async_client as client:
        response = await client.get("/system/config")

        assert response.status_code == 200

        data = response.json()

        assert "environment" in data
        assert "storage" in data
        assert "llm_provider" in data


@pytest.mark.asyncio
async def test_api_router_mounts(async_client):
    # sanity check geral do router
    async with async_client as client:
        response = await client.get("/health")

        assert response.status_code == 200
