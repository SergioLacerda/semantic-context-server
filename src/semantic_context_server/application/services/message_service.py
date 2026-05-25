import logging
from typing import Any

from semantic_context_server.application.contracts.response import Response
from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.ports.interaction_runtime import (
    InteractionRuntimePort,
)

logger = logging.getLogger("semantic_context_server.MessageService")


class MessageService:
    def __init__(
        self,
        deps: Any,
        executor: ExecutorPort,
        interaction_state: InteractionRuntimePort,
        settings: Any,
    ) -> None:
        """Initialize message service.

        Args:
            deps: Application dependencies
            executor: Async executor for task execution
            interaction_state: InteractionState for managing cooldown/locks/debounce
            settings: Application settings
        """
        self.deps = deps
        self.executor = executor
        self.interaction_state = interaction_state
        self.settings = settings

    # ---------------------------------------------------------
    # ENTRYPOINT
    # ---------------------------------------------------------
    async def handle(self, message: Any, ctx: Any, responder: Any) -> None:
        if message.author.bot:
            return

        content = (message.content or "").strip()
        if not content:
            return

        channel_id = ctx.channel.id
        user_id = ctx.author.id

        # ----------------------------------
        # COOLDOWN
        # ----------------------------------
        if not self.interaction_state.check_cooldown(user_id, 3):
            logger.debug("Cooldown active, skipping message")
            return

        # ----------------------------------
        # LOCK
        # ----------------------------------
        lock = self.interaction_state.get_lock(channel_id)
        if lock.locked():
            return

        # ----------------------------------
        # CAMPANHA
        # ----------------------------------
        campaign_id = await self.deps.campaign_state.get(channel_id)

        if not campaign_id:
            await responder.send("⚠️ Nenhuma campanha ativa.")
            return

        try:
            campaign = await self.deps.resolve_campaign(campaign_id)
        except Exception:
            logger.exception("Failed to resolve campaign")
            await responder.send("⚠️ Erro ao carregar campanha.")
            return

        async with lock:
            intent = await self._classify_intent(campaign, content, campaign_id)

            if intent == "OOC":
                return

            # ----------------------------------
            # EXECUÇÃO
            # ----------------------------------
            try:
                await self._execute_and_send(
                    responder,
                    campaign,
                    campaign_id,
                    content,
                    user_id,
                    intent,
                )
            except Exception:
                await responder.send("⚠️ Ocorreu um erro ao processar sua ação.")

    # ---------------------------------------------------------
    # INTENT
    # ---------------------------------------------------------
    async def _classify_intent(self, campaign: Any, content: str, campaign_id: str) -> str:
        try:
            try:
                result: str = await campaign.intent_classifier.classify(content, campaign_id)
                return result
            except TypeError:
                result = await campaign.intent_classifier.classify(content)
                return result
        except Exception:
            logger.exception("Intent classification failed")
            return "ACTION"

    # ---------------------------------------------------------
    # EXECUÇÃO
    # ---------------------------------------------------------
    async def _execute_and_send(
        self,
        responder: Any,
        campaign: Any,
        campaign_id: str,
        content: str,
        user_id: Any,
        intent: str,
    ) -> None:
        try:
            response = await campaign.narrative.execute(
                campaign_id=campaign_id,
                action=content,
                user_id=user_id,
            )
        except Exception:
            logger.exception("Narrative execution failed")
            raise

        if not response:
            return

        response = self._adapt_response_by_intent(response, intent)

        await self._send_response(responder, response)

    # ---------------------------------------------------------
    # ADAPTAÇÃO
    # ---------------------------------------------------------
    def _adapt_response_by_intent(self, response: Any, intent: Any) -> Response:
        if isinstance(response, Response):
            return response

        # Handle different response types: strings or objects with .content
        if isinstance(response, str):
            text = response
        elif hasattr(response, "content"):
            text = response.content
        else:
            text = str(response)

        return Response(
            text=text,
            type=str(intent).lower(),
        )

    # ---------------------------------------------------------
    # OUTPUT
    # ---------------------------------------------------------
    async def _send_response(self, responder: Any, response: Any) -> None:
        MAX = 1900

        if isinstance(response, Response):
            content = response.text
        else:
            content = response

        if not content:
            return

        if len(content) <= MAX:
            await responder.send(content)
            return

        for i in range(0, len(content), MAX):
            await responder.send(content[i : i + MAX])
