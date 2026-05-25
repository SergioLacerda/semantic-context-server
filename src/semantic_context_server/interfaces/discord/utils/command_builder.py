from typing import Any


async def dispatch_and_send(ctx: Any, dispatcher: Any, command: str) -> None:
    result = await dispatcher.dispatch(ctx, command)

    if result:
        await ctx.send(result)


def build_command(name: str, *args: str | None) -> str:
    parts = [name]

    for arg in args:
        if arg:
            parts.append(str(arg).strip())

    return " ".join(parts)
