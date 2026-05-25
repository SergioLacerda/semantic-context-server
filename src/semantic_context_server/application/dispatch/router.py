from typing import Any


class ApplicationRouter:
    def __init__(self, deps: Any, parser: Any, registry: Any) -> None:
        self.deps = deps
        self.parser = parser
        self.registry = registry

        # Mapeamento de intenções para comandos (extensível)
        self._intent_map = {
            "ACTION": "gm",
            "ROLL": "roll",
        }

    # ==========================================================
    # ENTRYPOINT
    # ==========================================================

    async def route(self, ctx: Any, input_text: str) -> list[Any]:
        # O parser pode ser sync (CPU bound leve), mas o roteamento é async
        parsed_commands = await self.deps.executor.run(self.parser.parse, input_text)

        if not parsed_commands:
            return [{"type": "unknown"}]

        routes = []

        for parsed in parsed_commands:
            route = await self._dispatch_parsed(ctx, parsed)
            routes.append(route)

        return routes

    # ==========================================================
    # CORE DISPATCH
    # ==========================================================

    async def _dispatch_parsed(self, ctx: Any, parsed: Any) -> dict[str, Any]:
        name = parsed.name

        # ------------------------------------------------------
        # FREE TEXT
        # ------------------------------------------------------
        if name == "__free_text__":
            return await self._handle_free_text(ctx, parsed.raw)

        # ------------------------------------------------------
        # COMMAND
        # ------------------------------------------------------
        command_cls = self.registry.get_command(name)

        if command_cls:
            return await self._build_command(ctx, command_cls, parsed)

        # ------------------------------------------------------
        # QUERY (NOVO 🔥)
        # ------------------------------------------------------
        query_cls = self.registry.resolve_query(name, parsed.args)

        if query_cls:
            return await self._build_query(ctx, query_cls, parsed)

        # ------------------------------------------------------
        # HELP (mantido)
        # ------------------------------------------------------
        if name == "help":
            return {"type": "help"}

        return {"type": "unknown"}

    # ==========================================================
    # BUILDERS
    # ==========================================================

    async def _build_command(self, ctx: Any, command_cls: Any, parsed: Any) -> dict[str, Any]:
        campaign_id = await self._get_campaign_id(ctx)

        if getattr(command_cls, "requires_campaign", False) and not campaign_id:
            return self._error("⚠️ Nenhuma campanha ativa.")

        if hasattr(command_cls, "from_parsed"):
            command = command_cls.from_parsed(parsed, ctx, campaign_id)
        else:
            command = command_cls(**self._build_kwargs(parsed, ctx, campaign_id))

        return {"type": "command", "command": command}

    async def _build_query(self, ctx: Any, query_cls: Any, parsed: Any) -> dict[str, Any]:
        campaign_id = await self._get_campaign_id(ctx)

        if hasattr(query_cls, "from_parsed"):
            query = query_cls.from_parsed(parsed, ctx, campaign_id)
        else:
            query = query_cls(campaign_id)

        return {"type": "query", "query": query}

    def _build_kwargs(self, parsed: Any, ctx: Any, campaign_id: str | None) -> dict[str, Any]:
        return {
            "args": parsed.args,
            "user_id": getattr(ctx.author, "id", None),
            "campaign_id": campaign_id,
        }

    # ==========================================================
    # FREE TEXT (mantido + melhorado)
    # ==========================================================

    async def _handle_free_text(self, ctx: Any, text: str) -> dict[str, Any]:
        campaign_id = await self._get_campaign_id(ctx)

        if not campaign_id:
            return {"type": "unknown"}

        campaign = await self.deps.resolve_campaign(campaign_id)
        intent = await campaign.intent_classifier.classify(text, campaign_id)
        command_name = self._intent_map.get(intent)

        if command_name:
            command_cls = self.registry.get_command(command_name)

            if command_cls:
                if hasattr(command_cls, "from_text"):
                    command = command_cls.from_text(
                        text=text,
                        ctx=ctx,
                        campaign_id=campaign_id,
                    )
                else:
                    command = command_cls(
                        campaign_id=campaign_id,
                        user_id=str(ctx.author.id),
                        action=text,
                    )

                return {"type": "command", "command": command}

        return {"type": "unknown"}

    # ==========================================================
    # HELPERS
    # ==========================================================

    async def _get_campaign_id(self, ctx: Any) -> str | None:
        # Async Mandate: Ports de estado devem ser aguardados
        state_port = self.deps.campaign_state
        result: str | None = await self.deps.executor.run(state_port.get, ctx.channel.id)
        return result

    def _error(self, message: str) -> dict[str, Any]:
        return {"type": "error", "message": message}
