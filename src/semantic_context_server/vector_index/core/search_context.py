from typing import Any


class SearchContext:
    def __init__(
        self,
        query: str,
        q_vec: list[float] | None,
        query_tokens: list[str],
        query_type: str | None,
        vector_store: Any,
        k: int = 4,
        token_store: Any | None = None,
        metadata_store: Any | None = None,
        ann: Any | None = None,
        temporal_index: Any | None = None,
    ) -> None:
        self.query = query
        self.q_vec = q_vec
        self.query_tokens = query_tokens
        self.query_type = query_type

        self.vector_store = vector_store
        self.token_store = token_store
        self.metadata_store = metadata_store

        self.k = k

        self.ann = ann
        self.temporal_index = temporal_index

        # 🔥 pipeline state
        self.candidates: list[Any] = []
        self.results: list[Any] = []

        # caches
        self._token_cache: dict[str, Any] = {}
        self._meta_cache: dict[str, Any] = {}

    # ==========================================================
    # VECTOR
    # ==========================================================
    def get_vector(self, doc_id: str) -> Any:
        if not self.vector_store:
            return None

        if hasattr(self.vector_store, "get"):
            return self.vector_store.get(doc_id)

        return None

    # ==========================================================
    # TOKENS (cached)
    # ==========================================================
    def get_tokens(self, doc_id: str) -> Any:
        if doc_id in self._token_cache:
            return self._token_cache[doc_id]

        tokens = None
        if self.token_store and hasattr(self.token_store, "get"):
            tokens = self.token_store.get(doc_id)

        self._token_cache[doc_id] = tokens
        return tokens

    # ==========================================================
    # METADATA (cached)
    # ==========================================================
    def get_metadata(self, doc_id: str) -> Any:
        if doc_id in self._meta_cache:
            return self._meta_cache[doc_id]

        meta = None
        if self.metadata_store and hasattr(self.metadata_store, "get"):
            meta = self.metadata_store.get(doc_id)

        self._meta_cache[doc_id] = meta
        return meta

    # ==========================================================
    # ADD RESULT (pipeline-safe)
    # ==========================================================
    def add_result(self, item: Any) -> None:
        if item is None:
            return

        self.results.append(item)

    # ==========================================================
    # ADD CANDIDATE
    # ==========================================================
    def add_candidate(self, item: Any) -> None:
        if item is None:
            return

        self.candidates.append(item)

    # ==========================================================
    # FINALIZE RESULTS
    # ==========================================================
    def finalize(self) -> "SearchContext":
        """
        Normaliza resultados finais para garantir:
        - presença de texto
        - deduplicação
        - limite k
        """

        seen = set()
        normalized = []

        for r in self.results:
            if isinstance(r, dict):
                text = r.get("text") or r.get("content") or ""
                score = r.get("score", 0.0)
            else:
                text = getattr(r, "text", str(r))
                score = getattr(r, "score", 0.0)

            if not text:
                continue

            if text in seen:
                continue
            seen.add(text)

            normalized.append(
                {
                    "text": text,
                    "score": float(score),
                }
            )

        normalized.sort(key=lambda x: x["score"], reverse=True)

        self.results = normalized[: self.k]

        return self
