import asyncio
import functools
from collections.abc import Callable
from typing import Any


def on_executor(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator para executar um método síncrono em um executor.
    Espera que a instância (self) possua um atributo 'executor'.
    Transforma o método em uma corrotina (async).
    """

    @functools.wraps(func)
    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        executor = getattr(self, "executor", None)

        # Se temos o nosso Executor global configurado
        if executor:
            return await executor.run(func, self, *args, **kwargs)

        # Fallback para o thread pool padrão do asyncio
        return await asyncio.to_thread(func, self, *args, **kwargs)

    return wrapper
