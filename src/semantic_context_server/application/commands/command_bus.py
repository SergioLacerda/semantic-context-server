from collections.abc import Awaitable, Callable
from typing import Any, Protocol

# ==========================================================
# TYPES
# ==========================================================


class CommandHandler(Protocol):
    async def handle(self, command: Any, ctx: Any | None = None) -> Any: ...


Middleware = Callable[
    [Any, Any, Callable[[], Awaitable[Any]]],
    Awaitable[Any],
]


# ==========================================================
# COMMAND BUS
# ==========================================================


class CommandBus:
    def __init__(self, registry: Any, middlewares: list[Middleware] | None = None) -> None:
        self.registry = registry
        self.middlewares = middlewares or []

    # ======================================================
    # DISPATCH
    # ======================================================

    async def dispatch(self, ctx: Any, command: Any) -> Any:
        handler: CommandHandler | None = self.registry.get(type(command))

        if not handler:
            raise ValueError(f"No handler for {type(command)}")

        async def final_handler() -> Any:
            return await handler.handle(command, ctx=ctx)

        pipeline = self._build_pipeline(final_handler, command, ctx)

        return await pipeline()

    # ======================================================
    # PIPELINE
    # ======================================================

    def _build_pipeline(self, final_handler: Any, command: Any, ctx: Any) -> Any:
        async def call_next(index: int) -> Any:
            if index < len(self.middlewares):
                middleware = self.middlewares[index]

                async def next_step() -> Any:
                    return await call_next(index + 1)

                return await middleware(
                    command,
                    ctx,
                    next_step,
                )

            return await final_handler()

        return lambda: call_next(0)
