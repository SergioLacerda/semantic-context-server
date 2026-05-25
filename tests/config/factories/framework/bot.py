from dataclasses import dataclass, field
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from semantic_context_server.application.commands.campaign.command import CampaignCommand
from semantic_context_server.application.commands.campaign.handler import CampaignCommandHandler
from semantic_context_server.application.commands.command_bus import CommandBus
from semantic_context_server.application.commands.command_registry import CommandRegistry
from semantic_context_server.application.commands.gm.command import GMCommand
from semantic_context_server.application.commands.gm.handler import GMCommandHandler
from semantic_context_server.application.commands.roll.command import RollCommand
from semantic_context_server.application.commands.roll.handler import RollCommandHandler
from semantic_context_server.application.commands.session.command import SessionCommand
from semantic_context_server.application.commands.session.handler import SessionCommandHandler
from semantic_context_server.frameworks.discord.bot import create_bot
from semantic_context_server.infrastructure.cache.base.base_cache import BaseCache
from tests.config.factories.framework.deps import make_deps
from tests.config.helpers.discord_factory import DummyExecutor, DummySettings

# =========================================================
# HARNESS
# =========================================================


@dataclass
class TestBotHarness:
    """
    Encapsula bot + infraestrutura de comando para testes.

    ✔ evita atributos dinâmicos
    ✔ facilita assertions
    ✔ mantém DI explícito
    """

    bot: Any
    bus: CommandBus
    registry: CommandRegistry
    _captured_command: Any = field(default=None, init=False, repr=False)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.bot, name)

    def hybrid_command(self, *args, **kwargs):
        """
        Captura a função do comando para execução direta nos testes de adaptadores.
        """

        def decorator(func):
            self._captured_command = func
            return func

        return decorator

    async def _command(self, ctx, command_name: str | None = None, **kwargs):
        """
        Executa o comando capturado ou resolve via registry para o CommandBus.
        """
        if self._captured_command:
            return await self._captured_command(ctx, **kwargs)

        if not command_name:
            raise ValueError("Um nome de comando ou comando capturado é necessário.")

        command_class = self.registry.get_command(command_name)
        if not command_class:
            raise ValueError(f"Comando '{command_name}' não encontrado no registro.")

        # Instancia o comando com os kwargs e despacha
        command_instance = command_class(**kwargs)
        return await self.bus.dispatch(ctx, command_instance)

    async def command(self, ctx, command_name: str | None = None, **kwargs):
        """Alias para _command para manter compatibilidade."""
        return await self._command(ctx, command_name=command_name, **kwargs)


# =========================================================
# FACTORY
# =========================================================


def make_bot(*, with_bus: bool = True, deps=None) -> TestBotHarness:
    """
    Cria bot de teste totalmente isolado.

    ✔ sem infra real
    ✔ com deps fake
    ✔ com CommandBus controlado
    """

    # -------------------------------------------------
    # DEPENDENCIES
    # -------------------------------------------------
    if deps is None:
        deps = make_deps()

    # -------------------------------------------------
    # BOT BASE (SEM COMMANDS)
    # -------------------------------------------------
    bot = create_bot(
        settings=DummySettings(),
        deps=deps,
        executor=MagicMock(),
        interaction_state=MagicMock(),
        register_commands=False,
    )

    # -------------------------------------------------
    # COMMAND SYSTEM
    # -------------------------------------------------
    registry = CommandRegistry()
    bus = CommandBus(registry)

    # -------------------------------------------------
    # REGISTER HANDLERS
    # -------------------------------------------------
    query_cache = BaseCache(kv_store=MagicMock(), ttl=3600)

    # Register campaign command handler
    query_bus = MagicMock()

    async def _dispatch_list_campaigns(*args, **kwargs):
        campaigns = await deps.list_campaigns()
        if not campaigns:
            return "Nenhuma campanha encontrada."
        return "\n".join(campaigns)

    query_bus.dispatch = AsyncMock(side_effect=_dispatch_list_campaigns)
    registry.register(
        CampaignCommand,
        CampaignCommandHandler(deps, query_bus, query_cache),
        name="campaign",
    )

    # Register roll command handler
    registry.register(
        RollCommand,
        RollCommandHandler(deps.resolve_campaign),
        name="roll",
    )

    # Register GM command handler
    registry.register(
        GMCommand,
        GMCommandHandler(deps, query_cache),
        name="gm",
    )

    # Register session command handler
    registry.register(
        SessionCommand,
        SessionCommandHandler(query_cache),
        name="endsession",
    )

    return TestBotHarness(
        bot=bot,
        bus=bus,
        registry=registry,
    )


# =========================================================
# EXECUTOR (helper isolado)
# =========================================================


def make_executor():
    return DummyExecutor()
