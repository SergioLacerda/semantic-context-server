import pytest

from semantic_context_server.interfaces.api.routes.health_controller import (
    health,
    ready,
)


class ReadyServiceTrue:
    async def is_ready(self):
        return True


class ReadyServiceFalse:
    async def is_ready(self):
        return False


class NoReadyService:
    pass


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_endpoint_default(client):
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] in ["ready", "loading"]


def test_health():
    result = health()

    assert result == {"status": "ok"}


@pytest.mark.asyncio
async def test_ready_true():
    service = ReadyServiceTrue()

    result = await ready(service)

    assert result == {"status": "ready"}


@pytest.mark.asyncio
async def test_ready_false():
    service = ReadyServiceFalse()

    result = await ready(service)

    assert result == {"status": "loading"}


@pytest.mark.asyncio
async def test_ready_without_method():
    service = NoReadyService()

    result = await ready(service)

    assert result == {"status": "ready"}
