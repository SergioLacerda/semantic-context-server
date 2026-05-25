import pytest

from semantic_context_server.application.commands.session.command import SessionCommand
from semantic_context_server.application.commands.session.handler import (
    SessionCommandHandler,
)


class DummyEndSessionUseCase:
    def __init__(self, result):
        self.result = result
        self.called_with = None

    async def execute(self, campaign_id):
        self.called_with = campaign_id
        return self.result


class DummyCampaign:
    def __init__(self, result):
        self.end_session = DummyEndSessionUseCase(result)


class DummyCache:
    def __init__(self):
        self.invalidated_prefixes = []

    async def invalidate_prefix(self, prefix):
        self.invalidated_prefixes.append(prefix)


def test_session_command_metadata_and_campaign_id():
    command = SessionCommand(campaign_id="camp1")

    assert command.name == "endsession"
    assert command.description == "Finaliza sessão"
    assert command.usage == "/endsession"
    assert command.category == "🛑 Sessão"
    assert command.campaign_id == "camp1"


@pytest.mark.asyncio
async def test_handler_returns_success_message_and_invalidates_cache():
    cache = DummyCache()
    handler = SessionCommandHandler(cache)

    command = SessionCommand(campaign_id="camp1")
    command.campaign = DummyCampaign("Resumo final")

    result = await handler.handle(command)

    assert result == "🛑 Sessão encerrada.\n\nResumo final"
    assert command.campaign.end_session.called_with == "camp1"
    assert cache.invalidated_prefixes == ["campaign:camp1"]


@pytest.mark.asyncio
async def test_handler_returns_warning_when_summary_is_empty():
    cache = DummyCache()
    handler = SessionCommandHandler(cache)

    command = SessionCommand(campaign_id="camp1")
    command.campaign = DummyCampaign(None)

    result = await handler.handle(command)

    assert result == "⚠️ Nenhum resumo gerado."
    assert command.campaign.end_session.called_with == "camp1"
    assert cache.invalidated_prefixes == ["campaign:camp1"]
