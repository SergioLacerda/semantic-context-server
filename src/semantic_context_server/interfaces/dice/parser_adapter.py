from typing import Any

from semantic_context_server.domain.dice.parser import DiceParser


class DiceParserAdapter:
    def __init__(self) -> None:
        self._parser = DiceParser()

    def parse(self, expression: str) -> Any:
        return self._parser.parse(expression)
