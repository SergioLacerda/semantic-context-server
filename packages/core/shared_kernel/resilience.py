from __future__ import annotations

import asyncio
import inspect
import logging
import random
from collections.abc import Callable
from typing import Any, TypeVar

logger = logging.getLogger("packages.core.shared_kernel.resilience")

T = TypeVar("T")


async def resilient_call(
    fn: Callable[..., Any],
    *args: Any,
    retries: int = 3,
    backoff: float = 1.5,
    base_delay: float = 0.1,
    max_delay: float = 10.0,
    timeout: float | None = None,
    executor: Any = None,
    **kwargs: Any,
) -> Any:
    delay = base_delay

    for attempt in range(1, retries + 1):
        try:
            if executor:
                result = executor.run(fn, *args, **kwargs)
            else:
                result = fn(*args, **kwargs)

            if inspect.isawaitable(result):
                if timeout:
                    return await asyncio.wait_for(result, timeout=timeout)
                return await result

            return result

        except asyncio.CancelledError:
            raise
        except Exception as e:
            fn_name = getattr(fn, "__name__", "callable")
            logger.warning("Attempt %s/%s failed for %s: %s", attempt, retries, fn_name, e)

            if attempt >= retries:
                raise

            jitter = random.uniform(0, delay * 0.1)
            await asyncio.sleep(delay + jitter)

            delay = min(delay * backoff, max_delay)
