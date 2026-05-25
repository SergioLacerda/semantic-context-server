import logging
from typing import Any

from semantic_context_server.application.commands.roll.command import RollCommand
from semantic_context_server.application.contracts.response import Response

logger = logging.getLogger(__name__)


class RollCommandHandler:
    def __init__(self, resolve_campaign: Any) -> None:
        self.resolve_campaign = resolve_campaign

    async def handle(self, command: RollCommand, ctx: Any = None) -> Any:
        expression = (command.expression or "").strip()

        if not expression:
            return self._error("Expressão inválida")

        try:
            # 🔥 resolve container da campanha
            container = await self.resolve_campaign(command.campaign_id)

            # 🔥 pega use case correto (isolado por campanha)
            usecase = container.roll_dice

            response = await usecase.execute(expression)

            return response

        except Exception:
            logger.exception("roll execution failed")
            return self._error("Erro ao rolar os dados")

    def _error(self, message: str) -> Response:
        return Response(
            text=message,
            type="error",
            metadata={"error": message},
        )
