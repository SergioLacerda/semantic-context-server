from collections.abc import Callable
from typing import Any


class ContextSelector:
    def __init__(
        self,
        max_tokens: int = 2000,
        token_counter: Callable[[list[str]], int] | None = None,
    ) -> None:
        self.max_tokens = max_tokens
        self.token_counter: Callable[[list[str]], int] = token_counter or (
            lambda tokens: len(tokens)
        )

    def select(self, docs: list[Any], tokenizer: Any) -> list[Any]:
        selected = []
        total_tokens = 0

        for doc in docs:
            text = self._extract_text(doc)

            tokens = tokenizer.tokenize(text)
            token_count = self.token_counter(tokens)

            if total_tokens + token_count > self.max_tokens:
                break

            selected.append(doc)
            total_tokens += token_count

        return selected

    # ---------------------------------------------------------
    # utils
    # ---------------------------------------------------------

    def _extract_text(self, doc: Any) -> str:
        if isinstance(doc, str):
            return doc

        if isinstance(doc, dict):
            return str(doc.get("text", ""))

        return str(doc)
