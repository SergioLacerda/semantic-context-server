import hashlib
import json
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any

from semantic_context_server.config.settings import settings


def _hash_request(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode()).hexdigest()


class CacheManager:
    """LRU in-memory cache backed by disk persistence."""

    def __init__(self) -> None:
        self._lru: OrderedDict[str, bytes] = OrderedDict()
        self._max_items: int = settings.cache.lru.max_items

    def _disk_path_for(self, key: str) -> Path:
        base = Path(settings.cache.disk.base_path)
        return base / key[:2] / key

    async def get(self, payload: dict[str, Any]) -> bytes | None:
        key = _hash_request(payload)

        if key in self._lru:
            self._lru.move_to_end(key)
            return self._lru[key]

        path = self._disk_path_for(key)
        if path.is_file():
            age = time.time() - path.stat().st_mtime
            if age < settings.cache.disk.ttl_seconds:
                data = path.read_bytes()
                self._store_lru(key, data)
                return data
            path.unlink(missing_ok=True)

        return None

    async def set(self, payload: dict[str, Any], data: bytes) -> None:
        key = _hash_request(payload)
        self._store_lru(key, data)

        path = self._disk_path_for(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def _store_lru(self, key: str, data: bytes) -> None:
        self._lru[key] = data
        self._lru.move_to_end(key)
        while len(self._lru) > self._max_items:
            self._lru.popitem(last=False)

    async def prune(self) -> None:
        base = Path(settings.cache.disk.base_path)
        if not base.exists():
            return
        now = time.time()
        ttl = settings.cache.disk.ttl_seconds
        for path in base.rglob("*"):
            if path.is_file() and (now - path.stat().st_mtime) > ttl:
                path.unlink(missing_ok=True)
