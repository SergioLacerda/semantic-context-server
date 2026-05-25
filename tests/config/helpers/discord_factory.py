from typing import Any


class DummyFollowup:
    def __init__(self, ctx):
        self.ctx = ctx

    async def send(self, content):
        self.ctx.sent_messages.append(content)


class DummyResponse:
    def __init__(self, ctx):
        self._done = False
        self.ctx = ctx

    def is_done(self):
        return self._done

    async def send_message(self, content):
        self._done = True
        self.ctx.sent_messages.append(content)

    async def defer(self, thinking=False):
        self._done = True

        if hasattr(self.ctx, "interaction"):
            self.ctx.interaction.deferred = True


class DummyInteraction:
    def __init__(self, ctx):
        self.response = DummyResponse(ctx)
        self.followup = DummyFollowup(ctx)
        self.deferred = False

    async def defer(self, thinking=False):
        self.deferred = True


class DummyChannel:
    def __init__(self, channel_id="channel1"):
        self.id = channel_id
        self.typing_called = False

    async def typing(self):
        self.typing_called = True

    async def send(self, content):
        pass


class DummyServices:
    def __init__(self):
        self.campaign_state = {}
        self.intent_classifier = None


class DummyAuthor:
    def __init__(self, user_id="user1"):
        self.id = user_id


class DummyGuild:
    def __init__(self, guild_id="guild1"):
        self.id = guild_id


class DummyBot:
    debug = True

    def __init__(self):
        self._command = None

    def hybrid_command(self, *args, **kwargs):
        def wrapper(fn):
            self._command = fn
            return fn

        return wrapper


class DummyUsecase:
    """
    Fake genérico para usecases.

    Permite:
    - retorno fixo
    - retorno dinâmico (callable)
    - simulação de erro
    - captura de chamadas
    """

    def __init__(self, result=None, error: Exception | None = None):
        self._result = result
        self._error = error

        self.calls: list[Any] = []

    async def execute(self, *args, **kwargs):
        self.calls.append(
            {
                "args": args,
                "kwargs": kwargs,
            }
        )

        if self._error:
            raise self._error

        if callable(self._result):
            return self._result(*args, **kwargs)

        return self._result


class DummyRuntimeSettings:
    environment = "test"
    profile = "local"
    device = None
    log_level = 20  # logging.INFO
    execution_timeout = 10
    max_cache_size = 10000
    executor_task_timeout = 300


class DummySettings:
    def __init__(self):
        self.runtime = DummyRuntimeSettings()


class DummyExecutor:
    def __init__(self, settings=None, debug=False):
        self.settings = settings
        self.debug = debug

    async def run(self, fn, *args, **kwargs):
        return await fn(*args, **kwargs)


class DummyCtx:
    def __init__(self, *, interaction=False):
        self.channel = DummyChannel()
        self.author = DummyAuthor()
        self.guild = DummyGuild()
        self.interaction = DummyInteraction(self) if interaction else None

        self.sent_messages = []

    async def send(self, content):
        self.sent_messages.append(content)

    async def defer(self):
        """Defer the command (no-op for tests)."""
        pass


# ----------------------------------------
# FACTORY
# ----------------------------------------


def make_ctx(*, interaction=False):
    return DummyCtx(interaction=interaction)
