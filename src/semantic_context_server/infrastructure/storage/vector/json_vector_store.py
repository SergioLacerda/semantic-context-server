from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

from packages.core.shared_kernel.json_utils import load_json, save_json
from semantic_context_server.infrastructure.storage.vector_store_config import (
    VectorStoreConfig,
)

# ---------------------------------------------------------
# STORE
# ---------------------------------------------------------


class JSONVectorStore:
    def __init__(self, path: Path, config: VectorStoreConfig | None = None) -> None:
        self.path = path
        self._cache: dict[str, list[float]] | None = None
        self.config = config or VectorStoreConfig()

    # ---------------------------------------------------------
    # INTERNAL
    # ---------------------------------------------------------

    @staticmethod
    def _get_file_size_kb(path: Path) -> float:
        if not path.exists():
            return 0.0
        return path.stat().st_size / 1024.0

    def _load(self) -> dict[str, list[float]]:
        if self._cache is None:
            self._cache = load_json(self.path, {})
        return self._cache

    def _persist(self) -> None:
        if self._cache is None:
            return

        self.path.parent.mkdir(parents=True, exist_ok=True)

        if self.config.enable_rotation:
            size_kb = self._get_file_size_kb(self.path)

            if size_kb > self.config.rotation_size or self._should_rotate(self._cache):
                self._rotate_file()

        save_json(self.path, self._cache)

    def _should_rotate(self, data: dict[str, Any]) -> bool:
        return len(data) > self.config.max_entries_per_file

    def _rotate_file(self) -> None:
        """
        Rotação segura:
        - renomeia arquivo atual
        - mantém cache atual
        """

        if not self.path.exists():
            return

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        rotated_path = self.path.with_name(f"{self.path.stem}_{timestamp}.json")

        self.path.rename(rotated_path)

    # ---------------------------------------------------------
    # API
    # ---------------------------------------------------------

    def add(self, doc_id: str, vector: Sequence[float]) -> None:
        data = self._load()
        data[doc_id] = list(vector)
        self._persist()

    def get(self, doc_id: str) -> list[float] | None:
        return self._load().get(doc_id)

    def keys(self) -> list[str]:
        return list(self._load().keys())

    def clear(self) -> None:
        self._cache = {}
        save_json(self.path, self._cache)

    # ---------------------------------------------------------
    # SEARCH (cosine similarity)
    # ---------------------------------------------------------

    def search(self, query_vector: Sequence[float], k: int) -> list[str]:
        data = self._load()

        if not data:
            return []

        q = np.array(query_vector)
        q_norm = np.linalg.norm(q) + 1e-8

        results: list[tuple[float, str]] = []

        for doc_id, vec in data.items():
            v = np.array(vec)
            v_norm = np.linalg.norm(v) + 1e-8

            score = float(np.dot(q, v) / (q_norm * v_norm))

            results.append((score, doc_id))

        results.sort(key=lambda x: x[0], reverse=True)

        return [doc_id for _, doc_id in results[:k]]
