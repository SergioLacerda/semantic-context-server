from typing import Protocol


class TextTokenizer(Protocol):
    def tokenize(self, text: str) -> list[str]: ...
