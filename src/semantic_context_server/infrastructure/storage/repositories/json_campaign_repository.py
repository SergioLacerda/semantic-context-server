import shutil
from pathlib import Path
from typing import Any

from packages.core.shared_kernel.json_utils import load_json, save_json
from semantic_context_server.application.ports.campaign_repository import (
    CampaignRepositoryPort,
)
from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.infrastructure.serialization.json_serializer import JSONSerializer


class JSONCampaignRepository(CampaignRepositoryPort):
    def __init__(self, base_path: Path, executor: ExecutorPort) -> None:
        # Centralização do path conforme o padrão de storage
        self.base_dir = base_path
        if self.base_dir.name != "campaigns":
            self.base_dir = base_path / "campaigns"

        self.executor = executor
        self.serializer = JSONSerializer()

    # ---------------------------------------------------------
    # helpers
    # ---------------------------------------------------------

    def _events_path(self, campaign_id: str) -> Path:
        return self.base_dir / str(campaign_id) / "events.json"

    def _sessions_path(self, campaign_id: str) -> Path:
        return self.base_dir / str(campaign_id) / "sessions.json"

    def _ensure_dir(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # IO
    # ---------------------------------------------------------

    async def load(self, path: Path) -> list[Any]:
        result: list[Any] = await self.executor.run(
            lambda: load_json(path, []) if path.exists() else []
        )
        return result

    async def save(self, path: Path, data: Any) -> None:
        def _save() -> None:
            self._ensure_dir(path)
            save_json(path, self.serializer.serialize(data))

        await self.executor.run(_save)

    # ---------------------------------------------------------
    # PORT
    # ---------------------------------------------------------

    async def get_events(self, campaign_id: str) -> list[Any]:
        return await self.load(self._events_path(campaign_id))

    async def save_events(self, campaign_id: str, events: list[Any]) -> None:
        await self.save(self._events_path(campaign_id), events)

    async def get_sessions(self, campaign_id: str) -> list[Any]:
        return await self.load(self._sessions_path(campaign_id))

    async def save_sessions(self, campaign_id: str, sessions: list[Any]) -> None:
        await self.save(self._sessions_path(campaign_id), sessions)

    def _campaign_dir(self, campaign_id: str) -> Path:
        return self.base_dir / str(campaign_id)

    async def create(self, campaign_id: str) -> None:
        await self.executor.run(
            lambda: self._campaign_dir(campaign_id).mkdir(parents=True, exist_ok=True)
        )

    async def list(self) -> list[str]:
        def _list() -> list[str]:
            if not self.base_dir.exists():
                return []
            return [p.name for p in self.base_dir.iterdir() if p.is_dir()]

        result: list[str] = await self.executor.run(_list)
        return result

    async def delete(self, campaign_id: str) -> None:
        def _delete() -> None:
            path = self._campaign_dir(campaign_id)
            if path.exists():
                shutil.rmtree(path)

        await self.executor.run(_delete)

    async def exists(self, campaign_id: str) -> bool:
        result: bool = await self.executor.run(lambda: self._campaign_dir(campaign_id).exists())
        return result
