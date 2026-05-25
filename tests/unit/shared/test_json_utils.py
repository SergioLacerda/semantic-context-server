import json
from pathlib import Path

from semantic_context_server.shared.json_utils import (
    load_json,
    save_json,
    update_json,
)
from tests.config.helpers.io import read_text_utf8, write_text_utf8


def test_load_json_creates_file(tmp_path):
    path = tmp_path / "file.json"

    result = load_json(path, default={"a": 1})

    assert result == {"a": 1}
    assert path.exists()


def test_load_json_reads_existing(tmp_path):
    path = tmp_path / "file.json"
    write_text_utf8(path, json.dumps({"x": 42}))

    result = load_json(path, default={})

    assert result == {"x": 42}


def test_load_json_corrupted_file(tmp_path):
    path = tmp_path / "file.json"
    write_text_utf8(path, "INVALID JSON")

    result = load_json(path, default={"ok": True})

    assert result == {"ok": True}

    assert json.loads(read_text_utf8(path)) == {"ok": True}

    backup = path.with_suffix(".json.corrupted")
    assert backup.exists()


def test_save_json_basic(tmp_path):
    path = tmp_path / "file.json"

    save_json(path, {"a": 1})

    data = json.loads(read_text_utf8(path))

    assert data == {"a": 1}


def test_save_json_with_set(tmp_path):
    path = tmp_path / "file.json"

    save_json(path, {"a": {1, 2}})

    data = json.loads(read_text_utf8(path))

    assert sorted(data["a"]) == [1, 2]


def test_update_json(tmp_path):
    path = tmp_path / "file.json"

    def updater(data):
        data["count"] = data.get("count", 0) + 1
        return data

    result = update_json(path, updater)

    assert result == {"count": 1}

    result = update_json(path, updater)

    assert result == {"count": 2}


def test_backup_failure_does_not_crash(monkeypatch, tmp_path):
    path = tmp_path / "file.json"
    write_text_utf8(path, "INVALID JSON")

    def fail_rename(*args, **kwargs):
        raise Exception("fail")

    monkeypatch.setattr(Path, "rename", fail_rename)

    result = load_json(path, default={"x": 1})

    assert result == {"x": 1}
