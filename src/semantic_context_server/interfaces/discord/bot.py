import logging
import traceback
from typing import Any

import discord
from discord.ext import commands

from semantic_context_server.application.commands.campaign.command import CampaignCommand
from semantic_context_server.application.commands.campaign.handler import CampaignCommandHandler
from semantic_context_server.application.commands.command_bus import CommandBus
from semantic_context_server.application.commands.command_registry import CommandRegistry
from semantic_context_server.application.commands.gm.command import GMCommand
from semantic_context_server.application.commands.gm.handler import GMCommandHandler
from semantic_context_server.application.commands.parser.command_parser import CommandParser
from semantic_context_server.application.commands.roll.command import RollCommand
from semantic_context_server.application.commands.roll.handler import RollCommandHandler
from semantic_context_server.application.commands.session.command import SessionCommand
from semantic_context_server.application.commands.session.handler import SessionCommandHandler
from semantic_context_server.application.dispatch.dispatcher import Dispatcher
from semantic_context_server.application.dispatch.middleware.campaign_middleware import (
    campaign_middleware,
)
from semantic_context_server.application.dispatch.middleware.error_middleware import (
    error_middleware,
)
from semantic_context_server.application.dispatch.middleware.logging_middleware import (
    logging_middleware,
)
from semantic_context_server.application.dispatch.middleware.timeout_middleware import (
    timeout_middleware,
)
from semantic_context_server.application.dispatch.router import ApplicationRouter
from semantic_context_server.application.queries.cache.query_cache import QueryCache
from semantic_context_server.application.queries.get_context_query import (
    GetContextQuery,
)
from semantic_context_server.application.queries.list_campaigns_query import (
    ListCampaignsQuery,
    ListCampaignsQueryHandler,
)
from semantic_context_server.application.queries.query_bus import QueryBus
from semantic_context_server.application.queries.query_registry import QueryRegistry
from semantic_context_server.application.services.message_service import MessageService
from semantic_context_server.interfaces.discord.adapters.campaign_commands import (
    register_campaign_commands,
)
from semantic_context_server.interfaces.discord.adapters.gm_commands import register_gm_commands
from semantic_context_server.interfaces.discord.adapters.help_commands import register_help_commands
from semantic_context_server.interfaces.discord.adapters.roll_commands import register_roll_command
from semantic_context_server.interfaces.discord.adapters.session_commands import (
    register_session_commands,
)
from semantic_context_server.interfaces.discord.bot_types import RPGDiscordBot
from semantic_context_server.interfaces.discord.context.message_context import MessageContext
from semantic_context_server.interfaces.discord.responder import DiscordResponder

logger = logging.getLogger("semantic_context_server.discord")


def create_bot(
    settings: Any, deps: Any, executor: Any, interaction_state: Any, register_commands: bool = True
) -> RPGDiscordBot:
    # ======================================================
    # DISCORD SETUP
    # ======================================================
    intents = discord.Intents.default()
    intents.message_content = True

    bot = RPGDiscordBot(command_prefix="!", intents=intents)
    bot.debug = settings.runtime.environment != "prod"
    bot.help_command = None
    bot.deps = deps

    # ======================================================
    # CACHE
    # ======================================================
    query_cache = QueryCache()

    # ======================================================
    # QUERY BUS
    # ======================================================
    query_bus = QueryBus()

    query_bus.register(
        ListCampaignsQuery,
        ListCampaignsQueryHandler(
            deps.list_campaigns,
            query_cache,
        ),
    )

    # ======================================================
    # QUERY REGISTRY
    # ======================================================
    query_registry = QueryRegistry()

    query_registry.register(GetContextQuery, "context")
    query_registry.register(ListCampaignsQuery, "campaign:list")

    # ======================================================
    # COMMAND REGISTRY
    # ======================================================
    registry = CommandRegistry()

    registry.register(
        GMCommand,
        GMCommandHandler(deps, query_cache),
        name="gm",
        meta={
            "description": "Executa ação narrativa",
            "usage": "!gm <ação>",
            "category": "🎭 Narrativa",
        },
    )

    registry.register(
        RollCommand,
        RollCommandHandler(deps.resolve_campaign),
        name="roll",
        meta={
            "description": "Rola dados",
            "usage": "/roll <expressão>",
            "category": "🎲 Dados",
        },
    )

    registry.register(
        SessionCommand,
        SessionCommandHandler(query_cache),
        name="endsession",
        meta={
            "description": "Finaliza sessão",
            "category": "🎭 Sessão",
        },
    )

    registry.register(
        CampaignCommand,
        CampaignCommandHandler(deps, query_bus, query_cache),
        name="campaign",
        meta={
            "description": "Gerencia campanhas",
            "usage": "/campaign <action>",
            "category": "🎭 Campanha",
        },
    )

    # ======================================================
    # COMMAND BUS
    # ======================================================
    command_bus = CommandBus(
        registry,
        middlewares=[
            campaign_middleware,
            logging_middleware,
            error_middleware,
            timeout_middleware,
        ],
    )

    # ======================================================
    # ROUTER (texto)
    # ======================================================
    parser = CommandParser()

    router = ApplicationRouter(
        deps=deps,
        parser=parser,
        registry=registry,
    )

    Dispatcher(
        deps,
        command_bus,
        query_bus,
        router,
    )

    # ======================================================
    # EVENTS
    # ======================================================
    @bot.event
    async def on_ready() -> None:
        logger.info(
            "Bot ready user=%s env=%s",
            bot.user,
            settings.runtime.environment,
        )

        try:
            await bot.tree.sync()
            logger.info("Slash commands synced")
        except Exception:
            logger.exception("Failed to sync commands")

    @bot.event
    async def on_command_error(ctx: Any, error: Any) -> None:
        responder = DiscordResponder(ctx)

        if isinstance(error, commands.CommandOnCooldown):
            await responder.send("⏳ Aguarde antes de usar novamente.")
            return

        logger.error("Command error: %s", error)
        traceback.print_exception(type(error), error, error.__traceback__)

        await responder.send("⚠️ Erro ao executar comando.")

    message_service = MessageService(
        deps=deps,
        executor=executor,
        interaction_state=interaction_state,
        settings=settings,
    )

    @bot.event
    async def on_message(message: Any) -> None:
        if message.author.bot:
            return

        ctx = MessageContext(message)
        responder = DiscordResponder(ctx)

        await responder.prepare()

        try:
            await message_service.handle(message, ctx, responder)
        except Exception:
            logger.exception("Message handling failed")
            await responder.send("⚠️ Erro inesperado.")

    # ======================================================
    # COMMAND REGISTRATION (SLASH)
    # ======================================================
    if register_commands:
        register_gm_commands(bot, command_bus)
        register_roll_command(bot, command_bus)
        register_session_commands(bot, command_bus)
        register_campaign_commands(bot, command_bus)
        register_help_commands(bot, registry)

    return bot
