from types import SimpleNamespace
from typing import Any

from semantic_context_server.application.ports.vector_reader_port import VectorReaderPort
from semantic_context_server.application.ports.vector_writer_port import VectorWriterPort
from semantic_context_server.infrastructure.rag.vector_reader_service import VectorReaderService
from semantic_context_server.infrastructure.rag.vector_writer_service import VectorWriterService


class RAGModule:
    @staticmethod
    def build(container: Any, ctx: Any) -> dict[str, Any]:
        try:
            reader_index = container.resolve(VectorReaderPort)
            writer_index = container.resolve(VectorWriterPort)
        except KeyError:

            class _NullVectorReader:
                async def search(
                    self,
                    campaign_id: str,
                    query: str,
                    k: int = 5,
                    filters: dict[str, Any] | None = None,
                ) -> list[dict[str, Any]]:
                    return []

            class _NullVectorWriter:
                async def store_event(
                    self, campaign_id: str, texts: list[str], metadata: dict
                ) -> None:
                    return None

            class _NullVectorIndex:
                def __init__(self) -> None:
                    class _NullDocumentStore:
                        async def get(self, key: str) -> dict | None:
                            return None

                    self.raw = SimpleNamespace(
                        components=SimpleNamespace(
                            vector_writer=_NullVectorWriter(),
                            vector_reader=_NullVectorReader(),
                            document_store=_NullDocumentStore(),
                        )
                    )

                async def index_campaign(
                    self,
                    campaign_id: str,
                    texts: list[str],
                    metadata: dict[str, Any] | None = None,
                ) -> None:
                    return None

                async def search(self, query: str, k: int = 4) -> list[dict]:
                    return []

                async def search_with_metadata(self, query: str, k: int = 4) -> list[dict]:
                    return []

            # Fallback para cenários sem wiring vetorial completo (ex.: testes unitários)
            return {
                "vector_reader": _NullVectorReader(),
                "vector_writer": _NullVectorWriter(),
                "vector_index": _NullVectorIndex(),
            }

        reader = VectorReaderService(vector_index=reader_index)
        writer = VectorWriterService(vector_index=writer_index, managed=True)

        return {
            "vector_reader": reader,
            "vector_writer": writer,
            "vector_index": writer_index,
        }
