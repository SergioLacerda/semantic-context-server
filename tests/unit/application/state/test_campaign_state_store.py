from unittest.mock import AsyncMock, MagicMock

import pytest

from semantic_context_server.application.state.campaign_state_store import (
    CampaignStateStore,
)
from semantic_context_server.infrastructure.storage.kv.json_kv_store import (
    JSONKeyValueStore,
)
from tests.config.helpers.io import read_text_utf8, write_text_utf8

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------


def make_store(tmp_path, content=None):
    path = tmp_path / "state.json"

    if content is not None:
        write_text_utf8(path, content)

    # Mock executor to handle async dispatch in unit tests
    executor = MagicMock(spec_set=["run"])

    async def mock_run(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    executor.run = AsyncMock(side_effect=mock_run)

    kv = JSONKeyValueStore(path, executor)
    return CampaignStateStore(kv), path


# ---------------------------------------------------------
# TESTES
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_load_valid_json(tmp_path):
    store, _ = make_store(tmp_path, '{"123": "campaign_a"}')

    assert await store.get("123") == "campaign_a"


@pytest.mark.asyncio
async def test_load_invalid_json_returns_empty(tmp_path):
    store, _ = make_store(tmp_path, "INVALID JSON")

    # Verificamos via API pública que o estado está vazio/limpo
    assert await store.get("any") is None


@pytest.mark.asyncio
async def test_save_writes_file(tmp_path):
    store, path = make_store(tmp_path)

    # Usamos o método set que agora gerencia a persistência de forma assíncrona
    await store.set("abc", "campaign_x")

    assert '"abc": "campaign_x"' in read_text_utf8(path)


@pytest.mark.asyncio
async def test_get_returns_none_when_missing(tmp_path):
    store, _ = make_store(tmp_path)

    assert await store.get("unknown") is None


@pytest.mark.asyncio
async def test_set_updates_and_persists(tmp_path):
    store, path = make_store(tmp_path)

    await store.set("channel_1", "campaign_1")

    # memória
    assert await store.get("channel_1") == "campaign_1"

    # persistência
    new_store, _ = make_store(tmp_path)
    assert await new_store.get("channel_1") == "campaign_1"


@pytest.mark.asyncio
async def test_set_overwrites_existing_value(tmp_path):
    store, _ = make_store(tmp_path)

    await store.set("channel_1", "campaign_1")
    await store.set("channel_1", "campaign_2")

    assert await store.get("channel_1") == "campaign_2"
