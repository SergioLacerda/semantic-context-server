from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve()
while PROJECT_ROOT != PROJECT_ROOT.parent and not (PROJECT_ROOT / "pyproject.toml").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.features.embedding_gateway import EmbeddingGatewayService  # noqa: E402


class FakeEmbeddingProvider:
    dimension = 3

    async def embed(self, text: str) -> list[float]:
        return [float(len(text)), 1.0, 0.0]


async def test_embedding_gateway_service_embed_and_batch() -> None:
    svc = EmbeddingGatewayService({"fake": FakeEmbeddingProvider()}, default_provider="fake")
    one = await svc.embed("abc")
    batch = await svc.embed_batch(["a", "ab"])
    assert one == [3.0, 1.0, 0.0]
    assert len(batch) == 2
