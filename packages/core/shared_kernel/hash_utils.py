from __future__ import annotations

import hashlib
import json


def normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().split()) if value else ""


def stable_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_hash(data: str | bytes | dict | list) -> str:
    if isinstance(data, bytes):
        raw = data
    elif isinstance(data, str):
        raw = data.encode("utf-8")
    elif isinstance(data, dict | list):
        raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    else:
        raise TypeError(f"Unsupported type for sha256_hash: {type(data)}")
    return hashlib.sha256(raw).hexdigest()
