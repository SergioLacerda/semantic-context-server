from __future__ import annotations

from typing import Any

from semantic_context_server.domain.dice.dice_engine import roll
from semantic_context_server.domain.dice.parser import DiceParser
from semantic_context_server.domain.dice.probability import analyze_distribution


class DomainDiceParserAdapter:
    def __init__(self) -> None:
        self._parser = DiceParser()

    def parse(self, expression: str) -> Any:
        return self._parser.parse(expression)


class DomainDiceRollerAdapter:
    def roll(self, ast: Any, rng: Any) -> tuple[list[int], int]:
        return roll(ast, rng)


class DomainDiceDistributionAnalyzerAdapter:
    def analyze(self, ast: Any) -> Any:
        return analyze_distribution(ast)

