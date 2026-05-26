import asyncio

import pytest

from packages.core.shared_kernel.resilience import resilient_call


@pytest.mark.slow
@pytest.mark.asyncio
async def test_resilient_call_with_timeout():
    async def slow():
        await asyncio.sleep(0.01)
        return "ok"

    result = await resilient_call(
        slow,
        timeout=1,
    )

    assert result == "ok"


@pytest.mark.asyncio
async def test_resilient_success():
    async def provider(x):
        return x + 1

    result = await resilient_call(provider, 1)

    assert result == 2


@pytest.mark.asyncio
async def test_resilient_retry():
    calls = {"n": 0}

    async def flaky(x):
        calls["n"] += 1
        if calls["n"] < 2:
            raise ValueError("fail")
        return x + 1

    result = await resilient_call(flaky, 1, retries=3)

    assert result == 2
    assert calls["n"] == 2


@pytest.mark.asyncio
async def test_resilient_fail_all():
    async def bad(x):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await resilient_call(bad, 1, retries=2)


@pytest.mark.slow
@pytest.mark.asyncio
async def test_resilient_timeout():
    async def slow(x):
        await asyncio.sleep(0.2)
        return x

    with pytest.raises(asyncio.TimeoutError):
        await resilient_call(slow, 1, timeout=0.05)


@pytest.mark.asyncio
async def test_resilient_sync_function():
    def sync_fn(x):
        return x + 5

    result = await resilient_call(sync_fn, 5)

    assert result == 10


@pytest.mark.asyncio
async def test_resilient_retry_exhausted():
    calls = {"n": 0}

    async def always_fail(x):
        calls["n"] += 1
        raise ValueError("fail")

    with pytest.raises(ValueError):
        await resilient_call(always_fail, 1, retries=3)

    assert calls["n"] == 3


@pytest.mark.asyncio
async def test_resilient_timeout_branch_success_explicit():
    async def async_fn():
        return "ok"

    result = await resilient_call(
        async_fn,
        timeout=1,
    )

    assert result == "ok"


@pytest.mark.slow
@pytest.mark.asyncio
async def test_resilient_timeout_branch_failure_explicit():
    async def async_fn():
        await asyncio.sleep(0.1)
        return "ok"

    with pytest.raises(asyncio.TimeoutError):
        await resilient_call(
            async_fn,
            timeout=0.01,
            retries=1,
        )


@pytest.mark.slow
@pytest.mark.asyncio
async def test_resilient_wait_for_branch_forced():
    async def slow():
        await asyncio.sleep(0)
        return "ok"

    result = await resilient_call(
        slow,
        timeout=1,
    )

    assert result == "ok"


@pytest.mark.slow
@pytest.mark.asyncio
async def test_resilient_wait_for_branch_strict():
    async def slow():
        await asyncio.sleep(0.001)
        return "ok"

    result = await resilient_call(
        slow,
        timeout=1,
    )

    assert result == "ok"


@pytest.mark.slow
@pytest.mark.asyncio
async def test_resilient_wait_for_branch_with_mock(monkeypatch):
    called = {"ok": False}

    async def fake_wait_for(coro, timeout):
        called["ok"] = True
        return await coro

    monkeypatch.setattr("asyncio.wait_for", fake_wait_for)

    async def slow():
        await asyncio.sleep(0)
        return "ok"

    result = await resilient_call(
        slow,
        timeout=1,
    )

    assert result == "ok"
    assert called["ok"] is True
