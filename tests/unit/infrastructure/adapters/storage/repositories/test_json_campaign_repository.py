from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from semantic_context_server.infrastructure.storage.repositories.json_campaign_repository import (
    JSONCampaignRepository,
)
from tests.config.helpers.io import write_text_utf8


@pytest.fixture
def executor():
    """
    Fixture que emula o comportamento do ExecutorPort.
    O objeto é síncrono, mas o método .run() é assíncrono.
    """
    mock = MagicMock(spec=["run"])

    async def mock_run(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    mock.run = AsyncMock(side_effect=mock_run)
    return mock


@pytest.mark.asyncio
class TestJSONCampaignRepository:
    def _repo(self, tmp_path: Path, executor):
        return JSONCampaignRepository(tmp_path, executor)

    async def test_load_returns_empty_if_file_not_exists(self, tmp_path, executor):
        repo = self._repo(tmp_path, executor)

        path = tmp_path / "missing.json"

        data = await repo.load(path)

        assert data == []

    async def test_save_and_load(self, tmp_path, executor):
        repo = self._repo(tmp_path, executor)

        path = tmp_path / "test.json"
        payload = [{"a": 1}]

        await repo.save(path, payload)
        result = await repo.load(path)

        assert result == payload

    async def test_load_invalid_json_returns_empty(self, tmp_path, executor):
        repo = self._repo(tmp_path, executor)

        path = tmp_path / "bad.json"
        write_text_utf8(path, "INVALID JSON")

        result = await repo.load(path)

        assert result == []

    async def test_save_and_get_events(self, tmp_path, executor):
        repo = self._repo(tmp_path, executor)

        await repo.save_events("c1", [{"event": 1}])

        events = await repo.get_events("c1")

        assert events == [{"event": 1}]

    async def test_get_events_empty(self, tmp_path, executor):
        repo = self._repo(tmp_path, executor)

        events = await repo.get_events("c1")

        assert events == []

    async def test_save_and_get_sessions(self, tmp_path, executor):
        repo = self._repo(tmp_path, executor)

        await repo.save_sessions("c1", [{"session": 1}])

        sessions = await repo.get_sessions("c1")

        assert sessions == [{"session": 1}]

    async def test_get_sessions_empty(self, tmp_path, executor):
        repo = self._repo(tmp_path, executor)

        sessions = await repo.get_sessions("c1")

        assert sessions == []

    async def test_create_campaign(self, tmp_path, executor):
        repo = self._repo(tmp_path, executor)

        await repo.create("c1")

        assert await repo.exists("c1") is True

    async def test_exists_false(self, tmp_path, executor):
        repo = self._repo(tmp_path, executor)

        assert await repo.exists("missing") is False

    async def test_list_campaigns(self, tmp_path, executor):
        repo = self._repo(tmp_path, executor)

        await repo.create("c1")
        await repo.create("c2")

        campaigns = await repo.list()

        assert set(campaigns) == {"c1", "c2"}

    async def test_list_empty(self, tmp_path, executor):
        repo = self._repo(tmp_path, executor)

        campaigns = await repo.list()

        assert campaigns == []

    async def test_delete_campaign(self, tmp_path, executor):
        repo = self._repo(tmp_path, executor)

        await repo.create("c1")

        assert await repo.exists("c1") is True

        await repo.delete("c1")

        assert await repo.exists("c1") is False

    async def test_delete_non_existing(self, tmp_path, executor):
        repo = self._repo(tmp_path, executor)

        await repo.delete("missing")

    async def test_full_flow(self, tmp_path, executor):
        repo = self._repo(tmp_path, executor)

        await repo.create("c1")

        await repo.save_events("c1", [{"e": 1}])
        await repo.save_sessions("c1", [{"s": 1}])

        events = await repo.get_events("c1")
        sessions = await repo.get_sessions("c1")

        assert events == [{"e": 1}]
        assert sessions == [{"s": 1}]
