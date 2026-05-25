from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from semantic_context_server.application.contracts.response import Response
from semantic_context_server.interfaces.api.dependencies import get_narrative_usecase
from semantic_context_server.interfaces.api.routes.narrative_controller import router


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router, prefix="/campaign")
    return app


@pytest.fixture
def mock_usecase():
    usecase = MagicMock()
    usecase.execute = AsyncMock(
        return_value=Response(
            text="You see an ancient altar ahead.",
            type="narrative",
            metadata={"intent": "exploration"},
        )
    )
    return usecase


@pytest.fixture
def override_narrative_dependency(app, mock_usecase):
    async def _mock_usecase():
        return mock_usecase

    app.dependency_overrides[get_narrative_usecase] = _mock_usecase

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def async_client(app):
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_narrative_event_success(
    async_client,
    mock_usecase,
    override_narrative_dependency,
):
    payload = {"action": "look around", "user_id": "user1"}

    async with async_client as client:
        response = await client.post("/campaign/test/event", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["response"]["type"] == "narrative"
    assert data["response"]["text"] == "You see an ancient altar ahead."

    mock_usecase.execute.assert_awaited_once_with(
        campaign_id="test",
        action="look around",
        user_id="user1",
    )


@pytest.mark.asyncio
async def test_narrative_event_validation_error(
    async_client,
    override_narrative_dependency,
):
    payload = {"action": "", "user_id": "user1"}

    async with async_client as client:
        response = await client.post("/campaign/test/event", json=payload)

    assert response.status_code == 422
