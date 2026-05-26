import hashlib
from typing import Any, cast

import pytest

from packages.core.shared_kernel.hash_utils import sha256_hash


def test_sha256_hash_with_string():
    data = "hello"
    expected = hashlib.sha256(data.encode("utf-8")).hexdigest()

    assert sha256_hash(data) == expected


def test_sha256_hash_with_bytes():
    data = b"hello"
    expected = hashlib.sha256(data).hexdigest()

    assert sha256_hash(data) == expected


def test_sha256_hash_same_input_same_output():
    data = "test"

    h1 = sha256_hash(data)
    h2 = sha256_hash(data)

    assert h1 == h2


def test_sha256_hash_str_vs_bytes_equivalent():
    text = "abc123"

    assert sha256_hash(text) == sha256_hash(text.encode("utf-8"))


def test_sha256_hash_empty_string():
    expected = hashlib.sha256(b"").hexdigest()

    assert sha256_hash("") == expected


def test_sha256_hash_empty_bytes():
    expected = hashlib.sha256(b"").hexdigest()

    assert sha256_hash(b"") == expected


def test_sha256_hash_unicode():
    data = "🔥 RPG Bot 🚀"
    expected = hashlib.sha256(data.encode("utf-8")).hexdigest()

    assert sha256_hash(data) == expected


def test_sha256_hash_invalid_type_int():
    with pytest.raises(TypeError):
        sha256_hash(cast(Any, 123))


def test_sha256_hash_invalid_type_object():
    with pytest.raises(TypeError):
        sha256_hash(cast(Any, object()))


def test_sha256_hash_str():
    assert sha256_hash("abc") == sha256_hash("abc")


def test_sha256_hash_bytes():
    assert sha256_hash(b"abc") == sha256_hash(b"abc")


def test_sha256_hash_dict_order_independent():
    d1 = {"a": 1, "b": 2}
    d2 = {"b": 2, "a": 1}

    assert sha256_hash(d1) == sha256_hash(d2)


def test_sha256_hash_list():
    assert sha256_hash([1, 2, 3]) == sha256_hash([1, 2, 3])
