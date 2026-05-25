from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class VectorIndexGateway(Protocol):
    """
    Port responsável por indexação e busca semântica por campanha.

    Este contrato define a interface que qualquer implementação de
    Vector Index deve seguir, independente da tecnologia usada
    (in-memory, FAISS, Chroma, etc).
    """

    # ==========================================================
    # INDEXAÇÃO
    # ==========================================================
    async def index_campaign(
        self,
        campaign_id: str,
        texts: list[str],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Indexa textos associados a uma campanha.

        Args:
            campaign_id: identificador da campanha
            texts: lista de textos a serem indexados
            metadata: metadados opcionais (ex: tipo, origem, etc)

        Notes:
            - Implementações devem ser idempotentes (evitar duplicação)
            - Deve suportar batch processing
        """
        ...

    # ==========================================================
    # BUSCA SEMÂNTICA
    # ==========================================================
    async def search(
        self,
        query: str,
        k: int = 4,
    ) -> list[dict]:
        """
        Executa busca semântica sobre o índice.

        Args:
            query: texto de busca
            k: número máximo de resultados

        Returns:
            Lista de resultados ordenados por relevância.

            Cada item deve conter pelo menos:
                {
                    "text": str,
                    "score": float (opcional, recomendado)
                }

        Notes:
            - Resultados devem estar ordenados por relevância
            - Implementações podem incluir campos extras (metadata, id, etc)
        """
        ...

    # ==========================================================
    # OPCIONAL (EXTENSÃO FUTURA)
    # ==========================================================
    async def search_with_metadata(
        self,
        query: str,
        k: int = 4,
    ) -> list[dict]:
        """
        (Opcional) Busca retornando metadados completos.

        Pode não ser implementado por todas as versões.
        """
        raise NotImplementedError
