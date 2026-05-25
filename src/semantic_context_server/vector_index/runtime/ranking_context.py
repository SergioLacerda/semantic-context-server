from collections.abc import Callable
from dataclasses import dataclass, field

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.ports.vector_reader_port import VectorReaderPort


@dataclass
class RankingContext:
    """
    Contexto de execução de uma busca no VectorIndex.
    Atua como um cache de curta duração para evitar processamento redundante.
    """

    query: str
    q_vec: list[float]
    vector_reader: VectorReaderPort
    executor: ExecutorPort

    # Tokenizador real (provido pelo VectorIndex)
    _tokenizer_fn: Callable[[str], list[str]] = field(repr=False)

    # Cache de tokens
    _query_tokens: set[str] = field(init=False)
    _doc_token_cache: dict[str, list[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Tokeniza a query imediatamente na criação do contexto
        if self.query and self._tokenizer_fn is not None:
            self._query_tokens = set(self._tokenizer_fn(self.query))

    @property
    def query_tokens(self) -> set[str]:
        """Retorna os tokens da query (cacheado)."""
        return self._query_tokens

    def get_tokens(self, doc_id: str) -> list[str]:
        """
        Obtém tokens de um documento.
        Se já foi tokenizado em um estágio anterior, retorna do cache.
        """
        if doc_id in self._doc_token_cache:
            return self._doc_token_cache[doc_id]

        # Se não estiver no cache, precisamos do texto bruto
        # Nota: O texto geralmente vem do document_store,
        # que deve ser acessado de forma eficiente.
        # Aqui, assumimos que o tokenizer_fn sabe buscar o texto se receber um doc_id
        # ou que o builder injetou uma função capaz disso.

        tokens = self._tokenizer_fn(doc_id)
        cached = list(tokens) if tokens else []
        self._doc_token_cache[doc_id] = cached
        return cached

    def get_batch_tokens(self, doc_ids: list[str]) -> list[list[str]]:
        """Otimização para buscar tokens de múltiplos documentos de uma vez."""
        return [self.get_tokens(doc_id) for doc_id in doc_ids]
