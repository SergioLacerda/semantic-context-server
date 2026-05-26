import math
from typing import Any

from packages.core.shared_kernel.hash_utils import sha256_hash
from packages.features.vector_index.contracts import VectorIndexGateway


# ==========================================================
# EMBEDDING
# ==========================================================
class FakeEmbeddingService:
    def __init__(self, dim: int = 32):
        self._dim = dim

    async def embed(self, text: str):
        digest = sha256_hash(text)

        values = [int(digest[i : i + 2], 16) / 255 for i in range(0, len(digest), 2)]

        return values[: self._dim]

    async def embed_batch(self, texts):
        return [await self.embed(t) for t in texts]


# ==========================================================
# SIMILARIDADE
# ==========================================================
def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


# ==========================================================
# FAKE VECTOR INDEX
# ==========================================================
class FakeVectorIndex(VectorIndexGateway):
    def __init__(self):
        self.embedding_service = FakeEmbeddingService()

        # 🔥 MULTI-CAMPAIGN
        self._vectors: dict[str, dict[str, list[float]]] = {}
        self._documents: dict[str, dict[str, dict]] = {}
        self._metadata: dict[str, dict[str, dict]] = {}

        self.calls: list[dict] = []

    # ------------------------------------------------------
    # INTERNAL
    # ------------------------------------------------------

    def _ensure_campaign(self, campaign_id: str):
        if campaign_id not in self._vectors:
            self._vectors[campaign_id] = {}
            self._documents[campaign_id] = {}
            self._metadata[campaign_id] = {}

    # ------------------------------------------------------
    # ADD
    # ------------------------------------------------------

    async def add(
        self,
        texts: list[str],
        metadata: list[dict[str, Any]] | None = None,
        *,
        campaign_id: str = "default",
    ):
        self.calls.append(
            {
                "op": "add",
                "campaign_id": campaign_id,
                "count": len(texts),
            }
        )

        self._ensure_campaign(campaign_id)

        metadata = metadata or [{} for _ in texts]

        vectors = await self.embedding_service.embed_batch(texts)

        for i, text in enumerate(texts):
            doc_id = sha256_hash(text)

            self._vectors[campaign_id][doc_id] = vectors[i]
            self._documents[campaign_id][doc_id] = {"text": text}
            self._metadata[campaign_id][doc_id] = metadata[i]

    # ------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------

    async def search(
        self,
        query: str,
        k: int = 4,
        q_vec: Any = None,
        *,
        campaign_id: str = "default",
    ):
        self.calls.append(
            {
                "op": "search",
                "campaign_id": campaign_id,
                "query": query,
            }
        )

        self._ensure_campaign(campaign_id)

        if q_vec is not None:
            query_vec = q_vec
        else:
            query_vec = await self.embedding_service.embed(query)

        scored = []

        for doc_id, vec in self._vectors[campaign_id].items():
            score = cosine_similarity(query_vec, vec)

            doc = self._documents[campaign_id].get(doc_id, {})
            metadata = self._metadata[campaign_id].get(doc_id)

            scored.append(
                {
                    "id": doc_id,
                    "text": doc.get("text", ""),
                    "score": score,
                    "metadata": metadata,
                }
            )

        scored.sort(key=lambda x: x["score"], reverse=True)

        return scored[:k]

    # ------------------------------------------------------
    # COMPAT (legacy support)
    # ------------------------------------------------------

    async def index_campaign(
        self,
        campaign_id: str,
        texts: list[str],
        metadata: dict[str, Any] | None = None,
    ):
        meta_list = None

        if metadata is not None:
            meta_list = [metadata for _ in texts]

        await self.add(
            campaign_id=campaign_id,
            texts=texts,
            metadata=meta_list,
        )

    async def search_async(self, query: str, k: int = 4):
        return await self.search(
            campaign_id="default",
            query=query,
            k=k,
        )

    async def search_with_metadata(
        self,
        query: str,
        k: int = 4,
    ) -> list[dict]:
        return await self.search(
            campaign_id="default",
            query=query,
            k=k,
        )
