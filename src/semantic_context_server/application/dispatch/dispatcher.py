from typing import Any


class Dispatcher:
    def __init__(self, deps: Any, command_bus: Any, query_bus: Any, router: Any) -> None:
        self.deps = deps
        self.command_bus = command_bus
        self.query_bus = query_bus
        self.router = router

    # ==========================================================
    # ENTRYPOINT
    # ==========================================================

    async def dispatch(self, ctx: Any, input_text: str) -> str:
        routes = await self.router.route(ctx, input_text)

        if not routes:
            return "🤔 Não entendi."

        results = []

        for route in routes:
            try:
                result = await self._handle_route(ctx, route)

                if result:
                    if hasattr(result, "text"):
                        result = result.text

                    results.append(result)

            except Exception as e:
                results.append(f"⚠️ Erro: {str(e)}")

        final = "\n".join(results)

        return final if final else "🤔 Não entendi."

    # ==========================================================
    # ROUTE HANDLER
    # ==========================================================

    async def _handle_query(self, ctx: Any, query: Any) -> Any:
        channel_id = ctx.channel.id

        campaign_id = self.deps.campaign_state.get(channel_id)

        # ------------------------------------------------------
        # GLOBAL QUERY (sem campanha)
        # ------------------------------------------------------
        if not campaign_id:
            return await self.query_bus.dispatch(query, ctx=ctx)

        # ------------------------------------------------------
        # CAMPAIGN-SCOPED QUERY 🔥
        # ------------------------------------------------------
        campaign = await self.deps.resolve_campaign(campaign_id)

        handler = campaign.query_handlers.get(type(query))

        if not handler:
            raise ValueError(f"No handler for {type(query)} in campaign")

        return await handler.handle(query, ctx=ctx)

    async def _handle_route(self, ctx: Any, route: dict[str, Any]) -> Any:
        rtype = route.get("type")

        # ------------------------------------------------------
        # ERROR
        # ------------------------------------------------------
        if rtype == "error":
            return route.get("message")

        # ------------------------------------------------------
        # HELP
        # ------------------------------------------------------
        if rtype == "help":
            return self._format_help()

        # ------------------------------------------------------
        # QUERY
        # ------------------------------------------------------
        if rtype == "query":
            return await self.query_bus.dispatch(route["query"], ctx=ctx)

        # ------------------------------------------------------
        # COMMAND
        # ------------------------------------------------------
        if rtype == "command":
            return await self.command_bus.dispatch(
                ctx,
                route["command"],
            )

        # ------------------------------------------------------
        # UNKNOWN
        # ------------------------------------------------------
        return "🤔 Não entendi."

    # ==========================================================
    # HELP
    # ==========================================================

    def _format_help(self) -> str:
        # Utiliza o registry centralizado conforme ia-rules.md (DRY)
        commands = self.router.registry.list_commands_meta()

        if not commands:
            return "⚠️ Nenhum comando disponível."

        lines = ["📖 **Comandos disponíveis:**\n"]

        current_category = None

        for cmd in commands:
            category = cmd.get("category", "Outros")

            if category != current_category:
                lines.append(f"\n{category}")
                current_category = category

            usage = cmd.get("usage", "")
            description = cmd.get("description", "")

            lines.append(f"• {usage} → {description}")

        return "\n".join(lines)
