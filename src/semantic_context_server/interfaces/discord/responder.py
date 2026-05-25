import logging
from typing import Any

from semantic_context_server.application.contracts.response import Response

logger = logging.getLogger(__name__)


class DiscordResponder:
    def __init__(self, ctx: Any) -> None:
        self.ctx = ctx

    async def prepare(self) -> None:
        interaction = getattr(self.ctx, "interaction", None)

        if interaction and not interaction.response.is_done():
            await interaction.response.defer(thinking=True)

    async def send(self, content: Any) -> None:
        if isinstance(content, Response):
            content = content.text

        interaction = getattr(self.ctx, "interaction", None)

        if interaction:
            try:
                await interaction.followup.send(content)
                return
            except Exception:
                logger.exception("Responder interaction failed")

        try:
            await self.ctx.send(content)
        except Exception:
            logger.exception("Responder ctx.send failed")
