# application/ports/dice_parser.py

from typing import Protocol, runtime_checkable

from semantic_context_server.domain.dice.ast.nodes import DiceNode


@runtime_checkable
class DiceParserPort(Protocol):
    def parse(self, expression: str) -> DiceNode: ...
