import logging
from typing import Any

from semantic_context_server.application.contracts.response import Response
from semantic_context_server.application.ports.dice_parser import DiceParserPort
from semantic_context_server.domain.dice.ast.nodes import RollNode
from semantic_context_server.domain.dice.dice_engine import roll
from semantic_context_server.domain.dice.probability import analyze_distribution
from semantic_context_server.domain.dice.value_objects import DiceExpression

logger = logging.getLogger(__name__)


class RollDiceUseCase:
    def __init__(
        self,
        rng: Any,
        parser: DiceParserPort,
        executor: Any = None,
        enable_analysis: bool = False,
    ) -> None:
        self.rng = rng
        self.parser = parser
        self.executor = executor
        self.enable_analysis = enable_analysis

    async def execute(self, expression: Any) -> Response:
        ast = await self._parse(expression)
        if isinstance(ast, Response):
            return ast

        try:
            if self.executor:
                rolls, total = await self.executor.run(roll, ast, self.rng)
            else:
                rolls, total = roll(ast, self.rng)
        except Exception as e:
            logger.error("Roll execution failed: %s", e, exc_info=True)
            return self._error("Roll execution failed")

        data = {"rolls": rolls, "total": total}
        if self.enable_analysis:
            data["distribution"] = await self._analyze(ast)

        return Response(text=self._format_text(data), type="dice", metadata=data)

    async def _parse(self, expression: Any) -> Any:
        try:
            if isinstance(expression, DiceExpression):
                return RollNode(expression.quantity, expression.sides)
            if isinstance(expression, str):
                ast = (
                    await self.executor.run(self.parser.parse, expression)
                    if self.executor
                    else self.parser.parse(expression)
                )
                return ast if ast is not None else self._error("Invalid dice expression")
            if hasattr(expression, "evaluate"):
                return expression
            return self._error("Invalid dice expression")
        except (ValueError, SyntaxError):
            logger.warning("Dice parsing failed for expression: %s", expression)
            return self._error("Invalid dice expression")

    async def _analyze(self, ast: Any) -> Any:
        try:
            if self.executor:
                return await self.executor.run(analyze_distribution, ast)
            return analyze_distribution(ast)
        except Exception:
            logger.warning("Distribution analysis failed", exc_info=True)
            return None

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def _error(self, message: str) -> Response:
        return Response(
            text=message,
            type="error",
            metadata={"error": message},
        )

    def _format_text(self, data: dict) -> str:
        rolls = ", ".join(map(str, data["rolls"]))
        total = data["total"]

        return f"🎲 Rolls: [{rolls}] → Total: {total}"
