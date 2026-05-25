import hashlib
import json


def sha256_hash(data: str | bytes | dict | list) -> str:
    """
    Gera hash SHA256 determinístico.

    Aceita apenas:
    - str
    - bytes
    - dict (ordenado)
    - list
    """

    # -----------------------------------------
    # bytes
    # -----------------------------------------
    if isinstance(data, bytes):
        raw = data

    # -----------------------------------------
    # string
    # -----------------------------------------
    elif isinstance(data, str):
        raw = data.encode("utf-8")

    # -----------------------------------------
    # estruturas determinísticas
    # -----------------------------------------
    elif isinstance(data, dict | list):
        raw = json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    # -----------------------------------------
    # inválido
    # -----------------------------------------
    else:
        raise TypeError(f"Unsupported type for sha256_hash: {type(data)}")

    return hashlib.sha256(raw).hexdigest()
