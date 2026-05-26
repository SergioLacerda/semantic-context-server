from packages.core.shared_kernel.json_utils import load_json, save_json
from tests.config.helpers.io import read_text_utf8, write_text_utf8


def test_load_json_file_not_exists(tmp_path):
    path = tmp_path / "file.json"

    result = load_json(path, default={})

    assert result == {}


def test_load_json_valid(tmp_path):
    path = tmp_path / "file.json"
    write_text_utf8(path, '{"a": 1}')

    result = load_json(path, default={})

    assert result["a"] == 1


def test_load_json_invalid(tmp_path):
    path = tmp_path / "file.json"
    write_text_utf8(path, "invalid json")

    result = load_json(path, default={})

    assert result == {}


def test_save_json(tmp_path):
    path = tmp_path / "dir" / "file.json"

    save_json(path, {"x": 1})

    assert path.exists()
    assert "x" in read_text_utf8(path)
