from collections.abc import Iterable


class ContextProvider:
    """
    Interface esperada:
    - get_context() -> dict[token, frequency]
    """

    def get_context(self) -> dict[str, int]:
        raise NotImplementedError


class ContextualScore:
    """
    Score baseado na frequência de termos no contexto recente.
    """

    def __init__(self, context_provider: ContextProvider):
        self.context_provider = context_provider

    # ---------------------------------------------------------
    # score único documento
    # ---------------------------------------------------------

    def score(self, doc_tokens: Iterable[str]) -> float:
        ctx = self.context_provider.get_context()

        if not ctx:
            return 0.0

        total = 0
        count = 0

        for token in doc_tokens:
            total += ctx.get(token, 0)
            count += 1

        if count == 0:
            return 0.0

        return total / count

    # ---------------------------------------------------------
    # score batch (útil para ranking)
    # ---------------------------------------------------------

    def batch_score(self, docs_tokens: list[Iterable[str]]) -> list[float]:
        ctx = self.context_provider.get_context()

        if not ctx:
            return [0.0] * len(docs_tokens)

        scores = []

        for tokens in docs_tokens:
            total = 0
            count = 0

            for t in tokens:
                total += ctx.get(t, 0)
                count += 1

            score = total / count if count else 0.0

            scores.append(score)

        return scores
