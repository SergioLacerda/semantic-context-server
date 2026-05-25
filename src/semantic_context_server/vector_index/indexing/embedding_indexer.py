from typing import Any


class EmbeddingIndexer:
    """
    Responsável por indexar documentos no VectorIndex.

    - gera embeddings
    - salva nos stores
    - integra com narrativa (opcional)
    """

    def __init__(
        self,
        embedding_client: Any,
        vector_store: Any,
        token_store: Any = None,
        metadata_store: Any = None,
        temporal_index: Any = None,
        causal_graph: Any = None,
    ) -> None:
        self.embedding = embedding_client

        self.vector_store = vector_store
        self.token_store = token_store
        self.metadata_store = metadata_store

        self.temporal_index = temporal_index
        self.causal_graph = causal_graph

    # ---------------------------------------------------------
    # API principal
    # ---------------------------------------------------------

    async def index_document(
        self,
        doc_id: str,
        text: str,
        tokens: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        timestamp: float | None = None,
        parent_id: str | None = None,
    ) -> None:
        """
        Indexa um documento completo.
        """

        if not text:
            return

        # ---------------------------------------------------------
        # embedding
        # ---------------------------------------------------------

        vector = await self.embedding.embed(text)

        # ---------------------------------------------------------
        # vector store
        # ---------------------------------------------------------

        self.vector_store.add(doc_id, vector)

        # ---------------------------------------------------------
        # tokens
        # ---------------------------------------------------------

        if tokens and self.token_store:
            self.token_store.set(doc_id, tokens)

        # ---------------------------------------------------------
        # metadata
        # ---------------------------------------------------------

        if metadata and self.metadata_store:
            self.metadata_store.set(doc_id, metadata)

        # ---------------------------------------------------------
        # timeline (🔥 narrativa)
        # ---------------------------------------------------------

        if self.temporal_index:
            self.temporal_index.add(doc_id, timestamp)

        # ---------------------------------------------------------
        # causal graph (🔥 narrativa)
        # ---------------------------------------------------------

        if self.causal_graph and parent_id:
            self.causal_graph.add_edge(parent_id, doc_id)

    # ---------------------------------------------------------
    # batch
    # ---------------------------------------------------------

    async def index_batch(self, documents: list[dict[str, Any]]) -> None:
        """
        Indexação em lote.
        """

        for doc in documents:
            await self.index_document(
                doc_id=doc["id"],
                text=doc["text"],
                tokens=doc.get("tokens"),
                metadata=doc.get("metadata"),
                timestamp=doc.get("timestamp"),
                parent_id=doc.get("parent_id"),
            )
