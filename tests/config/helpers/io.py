from pathlib import Path


def read_text_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text_utf8(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
