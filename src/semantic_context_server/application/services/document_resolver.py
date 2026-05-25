from typing import Any


class DocumentResolver:
    def __init__(self, document_store: Any, metadata_store: Any) -> None:
        self.document_store = document_store
        self.metadata_store = metadata_store

    def resolve(self, doc_ids: list[Any]) -> list[dict[str, Any]]:
        docs = []

        for doc_id in doc_ids:
            doc = self.document_store.get(doc_id) or {}
            meta = self.metadata_store.get(doc_id) or {}

            docs.append(
                {
                    "id": doc_id,
                    "text": doc.get("text", ""),
                    "score": meta.get("score", 0),
                    "metadata": meta,
                }
            )

        return docs
