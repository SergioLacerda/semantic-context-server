import json
import os
import tempfile
from pathlib import Path
from threading import RLock
from typing import Any, TypeVar

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.infrastructure.serialization.json_serializer import JSONSerializer
from semantic_context_server.shared.json_utils import load_json

T = TypeVar("T")


class JSONKeyValueStore:
    """
    KV store assíncrono baseado em JSON.

    ✔ API assíncrona (Async Mandate)
    ✔ escrita atômica (evita corrupção)
    ✔ lock em memória (thread-safe básico)
    ✔ suporte a serialização tipada
    """

    def __init__(self, path: Path, executor: ExecutorPort):
        self.path = path
        self.executor = executor
        self.serializer = JSONSerializer()
        self._lock = RLock()

    # ---------------------------------------------------------
    # INTERNAL
    # ---------------------------------------------------------

    def _read_all(self) -> dict[str, Any]:
        result: dict[str, Any] = load_json(self.path, {})
        return result

    def _write_all(self, data: dict[str, Any]) -> None:
        """
        Escrita atômica:
        - escreve em arquivo temporário
        - faz rename (atomic no POSIX)
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=self.path.parent,
        ) as tmp:
            json.dump(data, tmp, ensure_ascii=False, indent=2)
            temp_path = tmp.name

        os.replace(temp_path, self.path)

    # ---------------------------------------------------------
    # API
    # ---------------------------------------------------------

    async def get(self, key: str, cls: type[T] | None = None) -> Any:
        return await self.executor.run(self._get_sync, key, cls)

    def _get_sync(self, key: str, cls: type[T] | None = None) -> Any:
        with self._lock:
            data = self._read_all()
            value = data.get(key)
            if cls and value is not None:
                return self.serializer.deserialize(value, cls)
            return value

    async def set(self, key: str, value: Any) -> None:
        await self.executor.run(self._set_sync, key, value)

    def _set_sync(self, key: str, value: Any) -> None:
        with self._lock:
            data = self._read_all()
            data[key] = self.serializer.serialize(value)
            self._write_all(data)

    async def delete(self, key: str) -> None:
        await self.executor.run(self._delete_sync, key)

    def _delete_sync(self, key: str) -> None:
        with self._lock:
            data = self._read_all()
            data.pop(key, None)
            self._write_all(data)

    async def clear(self) -> None:
        await self.executor.run(self._clear_sync)

    def _clear_sync(self) -> None:
        with self._lock:
            self._write_all({})

    async def keys(self) -> list[str]:
        result: list[str] = await self.executor.run(self._keys_sync)
        return result

    def _keys_sync(self) -> list[str]:
        with self._lock:
            data = self._read_all()
            return list(data.keys())
