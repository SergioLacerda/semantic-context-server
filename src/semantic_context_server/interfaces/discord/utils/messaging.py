import logging

from discord.ext.commands import Context

from semantic_context_server.interfaces.discord.responder import DiscordResponder

logger = logging.getLogger("semantic_context_server.discord")

MAX_MESSAGE_LEN = 1900


async def send_long_response(
    ctx: Context,
    content: str,
    header: str = "",
) -> None:
    """
    Envia resposta longa com chunking seguro.
    """

    responder = DiscordResponder(ctx)

    if not content:
        await responder.send("Sem conteúdo para enviar.")
        return

    # ---------------------------------------
    # COM HEADER
    # ---------------------------------------
    if header:
        combined = header + content

        if len(combined) <= MAX_MESSAGE_LEN:
            await responder.send(combined)
            return

        await responder.send(header)
        content_to_send = content

    else:
        if len(content) <= MAX_MESSAGE_LEN:
            await responder.send(content)
            return

        content_to_send = content

    # ---------------------------------------
    # CHUNKING
    # ---------------------------------------
    for i in range(0, len(content_to_send), MAX_MESSAGE_LEN):
        chunk = content_to_send[i : i + MAX_MESSAGE_LEN]

        try:
            await responder.send(chunk)
        except Exception:
            logger.exception("Failed to send chunk")
