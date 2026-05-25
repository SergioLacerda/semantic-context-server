from typing import Any


class QueryBus:
    """
    Executor de queries (CQRS).
    Similar ao CommandBus, mas sem efeitos colaterais.
    """

    def __init__(self, middlewares: list[Any] | None = None) -> None:
        self._handlers: dict[type, Any] = {}
        self.middlewares: list[Any] = middlewares or []

    # ==========================================================
    # REGISTER
    # ==========================================================

    def register(self, query_type: type, handler: Any) -> None:
        if query_type in self._handlers:
            raise RuntimeError(f"Handler already registered for {query_type}")

        self._handlers[query_type] = handler

    # ==========================================================
    # DISPATCH
    # ==========================================================

    async def dispatch(self, query: Any, ctx: Any = None) -> Any:
        handler = self._resolve_handler(query)

        async def run() -> Any:
            return await handler.handle(query, ctx=ctx)

        pipeline = self._build_pipeline(run, query, ctx)

        return await pipeline()

    # ==========================================================
    # INTERNAL
    # ==========================================================

    def _resolve_handler(self, query: Any) -> Any:
        handler = self._handlers.get(type(query))

        if handler:
            return handler

        for t in self._handlers:
            if isinstance(query, t):
                return self._handlers[t]

        raise ValueError(f"No handler for {type(query)}")

    def _build_pipeline(self, final_handler: Any, query: Any, ctx: Any) -> Any:
        async def call_next(i: int) -> Any:
            if i < len(self.middlewares):
                middleware = self.middlewares[i]

                return await middleware(
                    query=query,
                    ctx=ctx,
                    next=lambda: call_next(i + 1),
                )

            return await final_handler()

        return lambda: call_next(0)
