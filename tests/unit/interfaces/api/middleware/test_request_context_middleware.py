from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import Request, Response

from semantic_context_server.interfaces.api import dependencies
from semantic_context_server.interfaces.api.middleware.request_context_middleware import (
    request_context_middleware,
)

# ==========================================================
# DUMMIES
# ==========================================================


class DummyCampaign:
    def __init__(self):
        self.narrative = "narrative"
        self.roll_dice = "dice"
        self.end_session = "end"


class DummyContainer:
    def __init__(self):
        self.event_bus = "bus"

        class Health:
            async def is_ready(self):
                return True

        self.health = Health()

        class Campaigns:
            async def get(self, campaign_id):
                return DummyCampaign()

        self.campaigns = Campaigns()


class FakeRequest(MagicMock):
    def __init__(self, container, campaign_id="test"):
        super().__init__(spec=Request)
        self.state = SimpleNamespace(
            container=container,
            campaign_id=campaign_id,
        )
        self.app = MagicMock()
        self.app.state = SimpleNamespace(container=container)


class DummyRequest(MagicMock):
    def __init__(self, path="/test", method="GET"):
        super().__init__(spec=Request)
        self.method = method
        self.url = MagicMock()
        self.url.path = path
        self.state = SimpleNamespace()
        self.app = MagicMock()
        self.app.state = SimpleNamespace(container=None)


# ==========================================================
# FIXTURES
# ==========================================================


@pytest.fixture
def fake_container(monkeypatch):
    container = DummyContainer()

    monkeypatch.setattr(
        dependencies,
        "get_container",
        lambda *args, **kwargs: container,
    )

    return container


# ==========================================================
# MIDDLEWARE
# ==========================================================


@pytest.mark.asyncio
async def test_request_context_success():
    async def call_next(request):
        return Response(status_code=200)

    response = await request_context_middleware(DummyRequest(), call_next)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_request_context_exception():
    async def call_next(request):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await request_context_middleware(DummyRequest(), call_next)


# ==========================================================
# DEPENDENCIES
# ==========================================================


@pytest.mark.asyncio
async def test_get_narrative(fake_container):
    request = FakeRequest(fake_container)

    result = await dependencies.get_narrative_usecase(request)
    assert result == "narrative"


@pytest.mark.asyncio
async def test_get_roll_dice(fake_container):
    request = FakeRequest(fake_container)

    result = await dependencies.get_roll_dice_usecase(request)
    assert result == "dice"


@pytest.mark.asyncio
async def test_get_end_session(fake_container):
    request = FakeRequest(fake_container)

    result = await dependencies.get_end_session_usecase(request)
    assert result == "end"


@pytest.mark.asyncio
async def test_get_event_bus(fake_container):
    request = FakeRequest(fake_container)

    result = await dependencies.get_event_bus(request)
    assert result == "bus"


@pytest.mark.asyncio
async def test_get_health_service(fake_container):
    request = FakeRequest(fake_container)

    service = await dependencies.get_health_service(request)

    assert await service.is_ready() is True


@pytest.mark.asyncio
async def test_get_health_service_fallback():
    request = FakeRequest(container=None)

    service = await dependencies.get_health_service(request)

    assert hasattr(service, "is_ready")
