import asyncio

import pytest

from packages.core.shared_kernel.logging_context import (
    get_request_id,
    set_request_id,
)


@pytest.mark.slow
@pytest.mark.asyncio
async def test_request_id_isolation():
    async def task1():
        set_request_id("t1")
        await asyncio.sleep(0)
        return get_request_id()

    async def task2():
        set_request_id("t2")
        await asyncio.sleep(0)
        return get_request_id()

    r1, r2 = await asyncio.gather(task1(), task2())

    assert r1 == "t1"
    assert r2 == "t2"


def test_get_request_id_default():
    assert get_request_id() == "-"


def test_set_and_get_request_id():
    set_request_id("abc-123")

    assert get_request_id() == "abc-123"
