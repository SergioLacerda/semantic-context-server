from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve()
while PROJECT_ROOT != PROJECT_ROOT.parent and not (PROJECT_ROOT / "pyproject.toml").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.features.semantic_cache import LegacySemanticCacheAdapter  # noqa: E402


async def test_legacy_adapter_roundtrip_with_variadic_key() -> None:
    cache = LegacySemanticCacheAdapter()

    await cache.set("campaign-1", "hello world", [1.0, 2.0], ["doc"])

    out = await cache.get("campaign-1", "  Hello   WORLD ", [1.0, 2.0])
    assert out == ["doc"]


async def test_legacy_adapter_search_and_store_aliases() -> None:
    cache = LegacySemanticCacheAdapter()

    await cache.store("q", (1, 2, 3), ["r"])
    out = await cache.search("q", (1, 2, 3))

    assert out == ["r"]
