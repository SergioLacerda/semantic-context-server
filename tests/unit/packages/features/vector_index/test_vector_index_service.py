from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve()
while PROJECT_ROOT != PROJECT_ROOT.parent and not (PROJECT_ROOT / "pyproject.toml").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.features.vector_index import VectorIndexService  # noqa: E402


class FakeEmbeddingGateway:
    async def embed(self, text: str):
        return [0.1, 0.2, float(len(text))]


class FakeVectorStore:
    async def search(self, vector, k: int):
        return [{"text": "doc", "score": 0.9, "k": k, "dim": len(vector)}]


async def test_vector_index_consumes_embedding_gateway_contract() -> None:
    svc = VectorIndexService(FakeEmbeddingGateway(), FakeVectorStore())
    out = await svc.search_by_text("query", k=3)
    assert out[0]["k"] == 3
    assert out[0]["dim"] == 3
