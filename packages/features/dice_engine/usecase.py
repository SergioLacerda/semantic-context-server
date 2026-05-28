from __future__ import annotations

import logging
from typing import Any, cast

from .contracts import (
    DiceDistributionAnalyzerContract,
    DiceParserContract,
    DiceResponse,
    DiceResponseMapperContract,
    DiceRollerContract,
)
from .domain.dice.ast.nodes import RollNode
from .domain.dice.value_objects import DiceExpression

logger = logging.getLogger(__name__)


class DefaultDiceResponseMapper(DiceResponseMapperContract):
    def map(self, rolls: list[int], total: int, distribution: Any | None) -> DiceResponse:
        metadata: dict[str, Any] = {"rolls": rolls, "total": total}
        if distribution is not None:
            metadata["distribution"] = distribution
        values = ", ".join(map(str, rolls))
        return DiceResponse(text=f"🎲 Rolls: [{values}] → Total: {total}", metadata=metadata)


class DiceUseCase:
    """Package-native dice orchestration: parse -> roll -> analyze -> response map."""

    def __init__(
        self,
        rng: Any,
        parser: DiceParserContract,
        roller: DiceRollerContract,
        analyzer: DiceDistributionAnalyzerContract | None = None,
        mapper: DiceResponseMapperContract | None = None,
        executor: Any = None,
        enable_analysis: bool = False,
    ) -> None:
        self.rng = rng
        self.parser = parser
        self.roller = roller
        self.analyzer = analyzer
        self.mapper = mapper or DefaultDiceResponseMapper()
        self.executor = executor
        self.enable_analysis = enable_analysis

    async def execute(self, expression: Any) -> DiceResponse:
        ast = await self._parse(expression)
        if isinstance(ast, DiceResponse):
            return ast

        try:
            rolls, total = await self._roll(ast)
        except Exception as exc:
            logger.error("Dice roll failed: %s", exc, exc_info=True)
            return self._error("Roll execution failed")

        distribution = await self._analyze(ast)
        return self.mapper.map(rolls, total, distribution)

    async def _parse(self, expression: Any) -> Any:
        try:
            if isinstance(expression, DiceExpression):
                return RollNode(expression.quantity, expression.sides)
            if isinstance(expression, str):
                ast = await self._run(self.parser.parse, expression)
                return ast if ast is not None else self._error("Invalid dice expression")
            if hasattr(expression, "evaluate"):
                return expression
            return self._error("Invalid dice expression")
        except (ValueError, SyntaxError):
            logger.warning("Dice parsing failed for expression: %s", expression)
            return self._error("Invalid dice expression")

    async def _roll(self, ast: Any) -> tuple[list[int], int]:
        return cast(tuple[list[int], int], await self._run(self.roller.roll, ast, self.rng))

    async def _analyze(self, ast: Any) -> Any | None:
        if not self.enable_analysis or self.analyzer is None:
            return None
        try:
            return await self._run(self.analyzer.analyze, ast)
        except Exception:
            logger.warning("Distribution analysis failed", exc_info=True)
            return None

    async def _run(self, fn: Any, *args: Any) -> Any:
        if self.executor:
            return await self.executor.run(fn, *args)
        return fn(*args)

    def _error(self, message: str) -> DiceResponse:
        return DiceResponse(text=message, type="error", metadata={"error": message})
