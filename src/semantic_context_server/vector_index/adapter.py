import asyncio
from typing import Any

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.ports.vector_index_gateway import VectorIndexGateway
from semantic_context_server.shared.hash_utils import sha256_hash


class VectorIndexAdapter(VectorIndexGateway):
    def __init__(self, engine: Any, executor: ExecutorPort) -> None:
        self._engine = engine
        self._executor = executor

    # ==========================================================
    # INDEX
    # ==========================================================
    async def index_campaign(
        self,
        campaign_id: str,
        texts: list[str],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        base_metadata = dict(metadata or {})
        service = self._engine.embedding_service

        if (embed_batch := getattr(service, "embed_batch", None)) and callable(embed_batch):
            embeddings = await self._executor.run(embed_batch, texts)
        else:
            tasks = [self._executor.run(service.embed, t) for t in texts]
            embeddings = await asyncio.gather(*tasks)

        components = self._engine.components

        for i, text in enumerate(texts):
            doc_id = f"{campaign_id}:{sha256_hash(text)}"

            # Verificação de existência agora é async conforme ia-rules.md
            if await components.document_store.get(doc_id):
                continue

            doc_metadata = {**base_metadata, "campaign_id": campaign_id}

            # Chamada transparente: pode ser o ChromaDB direto ou o VectorWriterService (batching)
            await components.vector_writer.add(doc_id, embeddings[i], doc_metadata)

            # Persistência nos stores KV seguindo o Async Mandate
            await components.document_store.set(
                doc_id,
                {"text": text, "campaign_id": campaign_id},
            )
            await components.metadata_store.set(doc_id, doc_metadata)

    # ==========================================================
    # SEARCH
    # ==========================================================

    async def search_with_metadata(self, query: str, k: int = 4) -> list[dict[str, Any]]:
        results = await self.search(query, k=k)
        return results

    async def search(
        self,
        query: str,
        k: int = 4,
    ) -> list[dict[str, Any]]:
        results = await self._engine.search(query, top_k=k)

        normalized: list[dict[str, Any]] = []
        for r in results:
            if isinstance(r, dict):
                normalized.append(r)
            else:
                normalized.append(
                    {
                        "text": getattr(r, "text", ""),
                    }
                )

        return normalized

    # ==========================================================
    # ESCAPE HATCH
    # ==========================================================
    @property
    def raw(self) -> Any:
        return self._engine
