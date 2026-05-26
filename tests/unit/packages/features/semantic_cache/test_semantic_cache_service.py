from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve()
while PROJECT_ROOT != PROJECT_ROOT.parent and not (PROJECT_ROOT / "pyproject.toml").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.features.semantic_cache import SemanticCacheService  # noqa: E402


async def test_semantic_cache_normalizes_prompt_keys() -> None:
    svc = SemanticCacheService()

    await svc.set("  Hello   WORLD ", {"value": 1})

    out = await svc.get("hello world")
    assert out == {"value": 1}


async def test_semantic_cache_invalidate_and_clear() -> None:
    svc = SemanticCacheService()

    await svc.set("a", 1)
    await svc.set("b", 2)
    await svc.invalidate("a")

    assert await svc.get("a") is None
    assert await svc.get("b") == 2

    await svc.clear()
    assert await svc.get("b") is None
