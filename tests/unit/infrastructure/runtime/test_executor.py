import asyncio

import pytest

from packages.core.bootstrap_runtime.concurrency.safe_executor import (
    ExecutorType,
)
from packages.core.bootstrap_runtime.concurrency.safe_executor import (
    SafeExecutor as Executor,
)

# ==========================================================
# HELPERS
# ==========================================================


def add_one(x):
    return x + 1


def add_two(x):
    return x + 2


def mul_two(x):
    return x * 2


def mul_three(x):
    return x * 3


# ==========================================================
# FIXTURES
# ==========================================================


@pytest.fixture
async def executor():
    exec = Executor()
    yield exec
    await exec.shutdown()


@pytest.fixture
async def thread_executor():
    exec = Executor(mode=ExecutorType.THREAD)
    yield exec
    await exec.shutdown()


@pytest.fixture
async def process_executor():
    exec = Executor(mode=ExecutorType.PROCESS)
    yield exec
    await exec.shutdown()


# ==========================================================
# TESTS - ASYNC (PADRÃO)
# ==========================================================


@pytest.mark.asyncio
async def test_executor_run_async(executor):
    result = await executor.run_async(lambda: 1)
    assert result == 1


@pytest.mark.asyncio
async def test_executor_multiple_tasks_async(executor):
    tasks = [executor.run_async(mul_two, i) for i in range(3)]
    results = await asyncio.gather(*tasks)

    assert results == [0, 2, 4]


@pytest.mark.asyncio
async def test_executor_run_thread(thread_executor):
    result = await thread_executor.run_async(lambda x: x + 1, 1)
    assert result == 2


@pytest.mark.asyncio
async def test_executor_run_process(process_executor):
    result = await process_executor.run_async(add_two, 2)
    assert result == 4


@pytest.mark.asyncio
async def test_executor_run_async_process(process_executor):
    result = await process_executor.run_async(mul_three, 3)
    assert result == 9


# ==========================================================
# LIFECYCLE
# ==========================================================


@pytest.mark.asyncio
async def test_executor_shutdown_idempotent():
    executor = Executor()

    await executor.shutdown()
    await executor.shutdown()  # não deve quebrar


@pytest.mark.asyncio
async def test_executor_shutdown_after_usage():
    executor = Executor()

    result = await executor.run_async(lambda: 1)
    assert result == 1

    await executor.shutdown()


# ==========================================================
# EDGE CASES
# ==========================================================


@pytest.mark.asyncio
async def test_executor_multiple_modes_isolated():
    thread_exec = Executor(mode=ExecutorType.THREAD)
    process_exec = Executor(mode=ExecutorType.PROCESS)

    result1 = await thread_exec.run_async(lambda: 1)
    result2 = await process_exec.run_async(add_two, 2)

    assert result1 == 1
    assert result2 == 4

    await thread_exec.shutdown()
    await process_exec.shutdown()
