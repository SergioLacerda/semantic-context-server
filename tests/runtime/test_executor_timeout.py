"""
Tests para P0-URGENT: Executor timeout prevention para zombie processes.

✔ Valida que tasks com timeout são canceladas
✔ Valida que TimeoutError é propagado
✔ Valida configuração via settings
"""

import asyncio
import time

import pytest

from packages.core.bootstrap_runtime.concurrency.safe_executor import ExecutorType
from packages.core.bootstrap_runtime.concurrency.safe_executor import SafeExecutor as Executor


@pytest.mark.asyncio
async def test_executor_timeout_on_infinite_task():
    """
    P0-URGENT: Validar que infinite tasks são canceladas após timeout.

    Este teste garante que zombie processes não ocorrem mesmo se
    uma task ficar em loop infinito.
    """
    executor = Executor(
        max_workers=2,
        mode=ExecutorType.THREAD,
        name="timeout_test",
        task_timeout=1.0,  # 1 segundo timeout
    )

    await executor.start()

    try:
        # Função que demora mais que o timeout
        def slow_task():
            time.sleep(5)  # 5 segundos (vai dar timeout após 1)
            return "done"

        with pytest.raises(TimeoutError) as exc_info:
            await executor.run(slow_task)

        assert "exceeded timeout" in str(exc_info.value)

    finally:
        await executor.shutdown()


@pytest.mark.asyncio
async def test_executor_without_timeout_completes():
    """Validar que tasks rapidinhas completam mesmo sem usar timeout."""
    executor = Executor(
        max_workers=2,
        mode=ExecutorType.THREAD,
        name="no_timeout_test",
        task_timeout=None,  # Sem timeout
    )

    await executor.start()

    def quick_task():
        return "completed"

    result = await executor.run(quick_task)
    assert result == "completed"

    await executor.shutdown()


@pytest.mark.asyncio
async def test_executor_timeout_config_from_settings(container_factory):
    """P0-URGENT: Validar que timeout é carregado via settings."""
    from packages.core.runtime_config.loader import load_settings

    settings = load_settings()

    # Validar que executor_task_timeout foi configurado
    assert hasattr(settings.runtime, "executor_task_timeout")
    assert settings.runtime.executor_task_timeout == 300  # Default 5 min


@pytest.mark.asyncio
async def test_executor_timeout_with_asyncio_task():
    """Validar timeout funciona também com async functions."""
    executor = Executor(
        max_workers=2, mode=ExecutorType.THREAD, name="async_timeout_test", task_timeout=1.0
    )

    await executor.start()

    try:

        async def async_slow():
            await asyncio.sleep(5)

        with pytest.raises(TimeoutError):
            await executor.run(async_slow)
    finally:
        await executor.shutdown()


@pytest.mark.asyncio
async def test_executor_timeout_propagates_in_shutdown():
    """
    P0-URGENT: Validar que pending tasks com timeout são limpos
    corretamente no shutdown.
    """
    executor = Executor(
        max_workers=1, mode=ExecutorType.THREAD, name="shutdown_timeout_test", task_timeout=2.0
    )

    await executor.start()

    # Iniciar varias tasks (uma vai dar timeout)
    def slow():
        time.sleep(3)

    # Tentar executar, vai dar timeout
    try:
        await executor.run(slow)
    except TimeoutError:
        pass

    # Shutdown deve ser limpo mesmo com timeout anterior
    await executor.shutdown()  # Não deve ficar pendurada
