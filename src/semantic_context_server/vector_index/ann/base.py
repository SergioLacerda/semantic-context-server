from typing import Protocol, runtime_checkable


@runtime_checkable
class ANN(Protocol):
    """
    Contrato universal de busca vetorial.

    🔥 Regras:
    - Sempre retorna IDs (str)
    - Nunca retorna objetos pesados
    """

    def search(self, query_vector: list[float], k: int = 10) -> list[str]: ...
