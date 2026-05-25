class RetrievalSelector:
    """
    Responsável por ordenar e selecionar documentos relevantes.
    NÃO conhece infra, apenas estrutura dos dados.
    """

    def select(self, docs: list[dict], limit: int = 10) -> list[dict]:
        if not docs:
            return []

        # ordena por score se existir
        docs = sorted(docs, key=lambda d: d.get("score", 0), reverse=True)

        return docs[:limit]

    def extract_texts(self, docs: list[dict]) -> list[str]:
        """
        Extrai apenas o texto dos documentos.
        """
        return [d.get("text", "") for d in docs if d.get("text")]

    def deduplicate(self, texts: list[str]) -> list[str]:
        """
        Remove duplicados mantendo ordem.
        """
        seen = set()
        result = []

        for t in texts:
            if t not in seen:
                seen.add(t)
                result.append(t)

        return result
