import inspect
from typing import Any

from semantic_context_server.application.ports.vector_reader_port import VectorReaderPort
from semantic_context_server.infrastructure.rag.retrieval_engine import RetrievalEngine


class VectorReaderService(VectorReaderPort):
    def __init__(
        self,
        vector_index: Any,
        executor: Any = None,
        embedding_cache: Any = None,
        semantic_cache: Any = None,
        document_store: Any = None,
        metadata_store: Any = None,
    ) -> None:
        # Hard Guard: Se o index for uma corrotina, o sistema falhou ao fazer o await no container
        if inspect.iscoroutine(vector_index):
            raise TypeError(
                "VectorReaderService received a coroutine as vector_index. "
                "Check if the StorageProvider.get() call is missing an 'await'."
            )

        self.executor = executor

        # Unwrapping para extrair o serviço de embedding do índice original
        engine = vector_index
        while hasattr(engine, "raw"):
            engine = engine.raw

        # Centraliza a inteligência de busca no RetrievalEngine
        self.engine = RetrievalEngine(
            vector_index=vector_index,
            embedding_service=getattr(engine, "embedding_service", None),
            embedding_cache=embedding_cache,
            semantic_cache=semantic_cache,
            executor=executor,
        )

        # Segurança: Garante que estamos acessando atributos de um objeto real, não de uma corrotina
        self.vector_store = getattr(engine, "vector_store", None)

        # Fallback seguro para o serviço de embedding
        self.embedding_service = getattr(engine, "embedding_service", None)
        if not self.embedding_service:
            # Se o engine for o RetrievalEngine, ele já tem o service.
            # Caso contrário, tentamos pegar do que foi injetado no motor.
            self.embedding_service = self.engine.embedding_service

        # Fallback para os stores do índice se não fornecidos explicitamente
        self.document_store = document_store or getattr(
            getattr(engine, "components", None), "document_store", None
        )
        self.metadata_store = metadata_store or getattr(
            getattr(engine, "components", None), "metadata_store", None
        )

    async def search(
        self,
        campaign_id: str,
        query: str,
        k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Realiza busca vetorial enriquecida com metadados.
        Utiliza o RetrievalEngine para caching e performance.
        """
        # O RetrievalEngine já lida com:
        # 1. Cache de embedding
        # 2. Cache semântico (query -> resultados)
        # 3. Execução via Executor (pool de threads)
        # 4. Deduplicação de buscas idênticas em voo
        results = await self.engine.search(query, k=k, campaign_id=campaign_id)

        if not results:
            return []

        # Enriquecimento de dados (Hydration)
        if self.executor:
            hydrated: list[dict[str, Any]] = await self.executor.run(
                self._hydrate_results, results, campaign_id
            )
            return hydrated

        return self._hydrate_results(results, campaign_id)

    def _hydrate_results(self, results: list[Any], campaign_id: str) -> list[dict[str, Any]]:
        """Processo síncrono de enriquecimento disparado via executor."""
        output: list[dict[str, Any]] = []

        # Narrowing para garantir segurança de tipo e evitar erro de 'None'
        doc_store = self.document_store
        meta_store = self.metadata_store

        if doc_store is None or meta_store is None:
            return output

        for item in results:
            # Suporta tanto o formato dict (padrão VectorIndex) quanto tupla (id, score)
            doc_id, score = (item.get("id"), item.get("score")) if isinstance(item, dict) else item

            doc = doc_store.get(doc_id)
            meta = meta_store.get(doc_id)

            if not doc or not meta:
                continue

            if meta.get("campaign_id") != campaign_id:
                continue

            output.append(
                {
                    "id": doc_id,
                    "text": doc.get("text"),
                    "metadata": meta,
                    "score": score,
                }
            )

        return output
