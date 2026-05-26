from pathlib import Path
from typing import Any

from packages.core.shared_kernel.json_utils import save_json

DEFAULT_FILES: dict[str, Any] = {
    "documents.json": {},
    "metadata.json": {},
    "vectors.json": {},
    "tokens.json": {},
}


def ensure_storage_structure(base: Path) -> None:
    base.mkdir(parents=True, exist_ok=True)

    for name, default in DEFAULT_FILES.items():
        path = base / name

        if not path.exists():
            save_json(path, default)


def ensure_memory_structure(base: Path) -> None:
    memory = base / "inmemory"
    memory.mkdir(parents=True, exist_ok=True)

    memory_files: dict[str, Any] = {
        "events.json": [],
        "narrative_graph.json": {},
        "response_cache.json": {},
    }

    for name, default in memory_files.items():
        path = memory / name

        if not path.exists():
            save_json(path, default)
