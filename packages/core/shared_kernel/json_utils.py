from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from packages.core.shared_kernel.text_io import read_text_utf8, write_text_utf8


def _backup_corrupted_file(path: Path) -> None:
    try:
        backup_path = path.with_suffix(path.suffix + ".corrupted")
        path.rename(backup_path)
    except Exception:
        pass


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        save_json(path, default)
        return default
    try:
        return json.loads(read_text_utf8(path))
    except Exception:
        _backup_corrupted_file(path)
        save_json(path, default)
        return default


def save_json(path: Path, data: Any) -> None:
    def _default(obj: Any) -> Any:
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        write_text_utf8(tmp_path, json.dumps(data, indent=2, ensure_ascii=False, default=_default))
        tmp_path.replace(path)
    except Exception as e:
        if tmp_path.exists():
            tmp_path.unlink()
        raise e


def update_json(path: Path, updater: Callable[[Any], Any]) -> Any:
    data = load_json(path, default={})
    new_data = updater(data)
    save_json(path, new_data)
    return new_data
