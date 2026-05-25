import json
from types import SimpleNamespace

import pytest

from semantic_context_server.interfaces.api.routes.campaign_controller import (
    create_campaign,
    delete_campaign,
    list_campaigns,
)

# ==========================================================
# MOCK CONTAINER
# ==========================================================


class MockCreate:
    def __init__(self, result):
        self.result = result

    async def execute(self, campaign_id):
        return self.result


class MockList:
    def __init__(self, result):
        self.result = result

    async def execute(self):
        return self.result


class MockDelete:
    def __init__(self, result):
        self.result = result

    async def execute(self, campaign_id):
        return self.result


def build_container(create=True, campaigns=None, delete=True):
    return SimpleNamespace(
        create_campaign=MockCreate(create),
        list_campaigns=MockList(campaigns),
        delete_campaign=MockDelete(delete),
    )


# ==========================================================
# CREATE
# ==========================================================


@pytest.mark.asyncio
async def test_create_campaign_success():
    container = build_container(create=True)

    response = await create_campaign("test", container)

    data = json.loads(response.body)

    assert "criada" in data["message"]


@pytest.mark.asyncio
async def test_create_campaign_already_exists():
    container = build_container(create=False)

    response = await create_campaign("test", container)

    data = json.loads(response.body)

    assert "já existe" in data["message"]


# ==========================================================
# LIST
# ==========================================================


@pytest.mark.asyncio
async def test_list_campaigns_empty():
    container = build_container(campaigns=[])

    response = await list_campaigns(container)

    data = json.loads(response.body)

    assert "Nenhuma campanha" in data["message"]


@pytest.mark.asyncio
async def test_list_campaigns_with_data():
    container = build_container(campaigns=["A", "B"])

    response = await list_campaigns(container)

    data = json.loads(response.body)

    assert "Campanhas:" in data["message"]
    assert "- A" in data["message"]
    assert "- B" in data["message"]


# ==========================================================
# DELETE
# ==========================================================


@pytest.mark.asyncio
async def test_delete_campaign_success():
    container = build_container(delete=True)

    response = await delete_campaign("test", container)

    data = json.loads(response.body)

    assert "removida" in data["message"]


@pytest.mark.asyncio
async def test_delete_campaign_not_found():
    container = build_container(delete=False)

    response = await delete_campaign("test", container)

    data = json.loads(response.body)

    assert "não encontrada" in data["message"]
