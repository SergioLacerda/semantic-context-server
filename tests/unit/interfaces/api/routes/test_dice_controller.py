from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from semantic_context_server.application.commands.roll.command import RollCommand
from semantic_context_server.application.contracts.response import Response
from semantic_context_server.interfaces.api.routes.dice_controller import (
    _campaign,
    router,
)

# ==========================================================
# APP FIXTURE (🔥 GARANTE ROTA)
# ==========================================================


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)  # 🔥 ESSENCIAL
    return app


# ==========================================================
# MOCKS
# ==========================================================


@pytest.fixture
def mock_command_bus():
    bus = MagicMock()
    bus.execute = AsyncMock()
    return bus


@pytest.fixture
def mock_campaign(mock_command_bus):
    campaign = MagicMock()
    campaign.command_bus = mock_command_bus
    return campaign


# ==========================================================
# DEPENDENCY OVERRIDE (🔥 CORRETO)
# ==========================================================


@pytest.fixture
def override_campaign_dependency(app, mock_campaign):
    async def _mock_campaign():
        return mock_campaign

    app.dependency_overrides[_campaign] = _mock_campaign

    yield

    app.dependency_overrides.clear()


# ==========================================================
# CLIENT
# ==========================================================


@pytest.fixture
def async_client(app):
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


# ==========================================================
# TESTS
# ==========================================================


@pytest.mark.asyncio
async def test_roll_success(async_client, mock_command_bus, override_campaign_dependency):
    mock_command_bus.execute.return_value = Response(
        text="🎲 Rolls: [4, 5] → Total: 9",
        type="dice",
        metadata={"rolls": [4, 5], "total": 9},
    )

    async with async_client as client:
        response = await client.post(
            "/dice/roll",
            json={"expression": "2d6", "user_id": 1},
        )

    assert response.status_code == 200

    data = response.json()

    assert data["type"] == "dice"
    assert data["metadata"]["total"] == 9

    mock_command_bus.execute.assert_called_once()
    command = mock_command_bus.execute.call_args[0][0]

    assert isinstance(command, RollCommand)
    assert command.expression == "2d6"


@pytest.mark.asyncio
async def test_roll_invalid_expression(
    async_client, mock_command_bus, override_campaign_dependency
):
    mock_command_bus.execute.return_value = Response(
        text="Invalid dice expression",
        type="error",
        metadata={"error": "Invalid dice expression"},
    )

    async with async_client as client:
        response = await client.post(
            "/dice/roll",
            json={"expression": "", "user_id": 1},
        )

    assert response.status_code == 200

    data = response.json()

    assert data["type"] == "error"


@pytest.mark.asyncio
async def test_roll_command_bus_failure(
    async_client, mock_command_bus, override_campaign_dependency
):
    mock_command_bus.execute.side_effect = Exception("boom")

    async with async_client as client:
        response = await client.post(
            "/dice/roll",
            json={"expression": "1d20", "user_id": 1},
        )

    assert response.status_code == 500

    data = response.json()

    assert data["detail"]["type"] == "error"


@pytest.mark.asyncio
async def test_roll_missing_expression(async_client, override_campaign_dependency):
    async with async_client as client:
        response = await client.post(
            "/dice/roll",
            json={},
        )

    assert response.status_code == 422
