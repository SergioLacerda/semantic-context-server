import asyncio
import functools
from collections.abc import Callable
from typing import Any


def spy_on(func: Callable) -> Callable:
    """
    Decorator World Class para Fakes.
    Automatiza o registro de chamadas em self.calls de forma transparente.
    Suporta métodos síncronos e assíncronos.
    """

    @functools.wraps(func)
    async def async_wrapper(self, *args, **kwargs):
        _record_call(self, func.__name__, *args, **kwargs)
        return await func(self, *args, **kwargs)

    @functools.wraps(func)
    def sync_wrapper(self, *args, **kwargs):
        _record_call(self, func.__name__, *args, **kwargs)
        return func(self, *args, **kwargs)

    def _record_call(instance: Any, name: str, *args, **kwargs):
        if not hasattr(instance, "calls"):
            instance.calls = []

        instance.calls.append(
            {
                "method": name,
                "args": args,
                "kwargs": kwargs,
                "type": name,  # Mantém compatibilidade com padrão anterior
            }
        )

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
