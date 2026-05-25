class TestCtx:
    """
    Contexto padrão para testes de Discord.

    Compatível com:
    - send()
    - interaction
    - channel / guild / author
    """

    def __init__(
        self,
        *,
        user_id="user_1",
        channel_id="channel_1",
        guild_id="guild_1",
        interaction=False,
    ):
        # ----------------------------------
        # IDENTIDADE
        # ----------------------------------
        self.user_id = user_id
        self.channel_id = channel_id

        # discord-like objects
        self.author = type("Author", (), {"id": user_id})
        self.channel = type("Channel", (), {"id": channel_id})
        self.guild = type("Guild", (), {"id": guild_id})

        # ----------------------------------
        # MENSAGENS
        # ----------------------------------
        self.sent_messages: list[str] = []

        # compat legacy
        self.sent = self.sent_messages

        # ----------------------------------
        # INTERACTION (slash commands)
        # ----------------------------------
        self.interaction = None

        if interaction:
            self.interaction = DummyInteraction()

    # ----------------------------------
    # DISCORD API
    # ----------------------------------

    async def send(self, msg):
        self.sent_messages.append(msg)

    # ----------------------------------
    # HELPERS DE TESTE
    # ----------------------------------

    def last_message(self):
        if not self.sent_messages:
            return None
        return self.sent_messages[-1]

    def assert_sent(self, text=None):
        assert self.sent_messages, "Nenhuma mensagem enviada"

        if text:
            assert text in self.sent_messages[-1]


# ---------------------------------------------------------
# INTERACTION
# ---------------------------------------------------------


class DummyInteraction:
    def __init__(self):
        self.deferred = False
        self.response = DummyResponse()

    async def defer(self):
        self.deferred = True


class DummyResponse:
    async def send_message(self, content):
        pass


# ---------------------------------------------------------
# FACTORY (compatível com seu padrão atual)
# ---------------------------------------------------------


def make_ctx(*, interaction=False, **kwargs):
    return TestCtx(interaction=interaction, **kwargs)
