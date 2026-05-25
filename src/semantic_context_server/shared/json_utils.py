import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from semantic_context_server.shared.text_io import read_text_utf8, write_text_utf8

# ---------------------------------------------------------
# load
# ---------------------------------------------------------


def _backup_corrupted_file(path: Path) -> None:
    try:
        backup_path = path.with_suffix(path.suffix + ".corrupted")
        path.rename(backup_path)
    except Exception:
        pass


def load_json(path: Path, default: Any) -> Any:
    # ---------------------------------------------------------
    # 1. arquivo não existe → cria
    # ---------------------------------------------------------
    if not path.exists():
        save_json(path, default)
        return default

    # ---------------------------------------------------------
    # 2. tentar carregar
    # ---------------------------------------------------------
    try:
        return json.loads(read_text_utf8(path))

    # ---------------------------------------------------------
    # 3. arquivo corrompido → recuperar
    # ---------------------------------------------------------
    except Exception:
        _backup_corrupted_file(path)
        save_json(path, default)
        return default


# ---------------------------------------------------------
# save
# ---------------------------------------------------------


def save_json(path: Path, data: Any) -> None:
    def _default(obj: Any) -> Any:
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    path.parent.mkdir(parents=True, exist_ok=True)

    # Escrita Atômica: Salva em um arquivo temporário e substitui o original.
    # Isso previne corrupção de dados se o processo cair durante a gravação.
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        write_text_utf8(tmp_path, json.dumps(data, indent=2, ensure_ascii=False, default=_default))

        # replace é atômico na maioria dos sistemas de arquivos modernos
        tmp_path.replace(path)
    except Exception as e:
        if tmp_path.exists():
            tmp_path.unlink()
        raise e


# ---------------------------------------------------------
# update (helper útil)
# ---------------------------------------------------------


def update_json(path: Path, updater: Callable[[Any], Any]) -> Any:
    data = load_json(path, default={})

    new_data = updater(data)

    save_json(path, new_data)

    return new_data
