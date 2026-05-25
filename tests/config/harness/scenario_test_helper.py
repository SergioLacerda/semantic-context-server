import asyncio
import time
from collections.abc import Callable
from typing import Any

from tests.config.harness.scenario_harness import ScenarioHarness


class ScenarioTestHelper:
    """
    Helper para testes de cenário.

    ✔ remove boilerplate de factory
    ✔ encapsula acesso async ao container
    ✔ fornece helpers de alto nível
    ✔ mantém compatibilidade com arquitetura atual
    """

    def __init__(self, container_factory: Callable[..., Any]):
        self._factory = container_factory
        self._scenario = ScenarioHarness()

    # ---------------------------------------------------------
    # SCENARIO EXECUTION
    # ---------------------------------------------------------

    async def run(
        self,
        actions: list[str],
        *,
        campaign_id: str = "test",
        user_id: str = "u1",
    ):
        return await self._scenario.run_scenario(
            actions,
            campaign_id=campaign_id,
            user_id=user_id,
            container_factory=self._factory,
        )

    async def step(
        self,
        action: str,
        *,
        campaign_id: str = "test",
        user_id: str = "u1",
    ):
        return await self._scenario.run_step(
            campaign_id=campaign_id,
            action=action,
            user_id=user_id,
            container_factory=self._factory,
        )

    # ---------------------------------------------------------
    # CONTAINER ACCESS
    # ---------------------------------------------------------

    async def container(self, campaign_id: str = "test"):
        return await self._scenario.get_container(
            campaign_id,
            factory=self._factory,
        )

    async def memory(self, campaign_id: str = "test"):
        container = await self.container(campaign_id)
        return await container.memory_service.load_memory(campaign_id)

    async def narrative(self, campaign_id: str = "test"):
        container = await self.container(campaign_id)
        return container.narrative

    async def wait_for(
        self,
        condition,
        *,
        timeout=5.0,
        interval=0.1,
    ):
        start = time.time()

        while True:
            if await condition():
                return

            if time.time() - start > timeout:
                raise TimeoutError("Condition not met")

            await asyncio.sleep(interval)

    async def wait_for_memory(
        self,
        keyword: str,
        *,
        campaign_id: str = "test",
        timeout: float = 5.0,
        interval: float = 0.1,
    ):
        """
        Aguarda até que a memória contenha a keyword.

        ✔ suporta consistência eventual (async pipelines)
        ✔ evita flaky tests
        ✔ timeout configurável
        """

        start = time.time()
        keyword = keyword.lower()

        while True:
            memory = await self.memory(campaign_id)
            text = " ".join(memory.recent_events).lower()

            if keyword in text:
                return

            if time.time() - start > timeout:
                raise TimeoutError(
                    f"Memory did not contain '{keyword}' after {timeout}s.\nCurrent memory:\n{text}"
                )

            await asyncio.sleep(interval)

    # ---------------------------------------------------------
    # RESULTS
    # ---------------------------------------------------------

    def last(self):
        return self._scenario.last_result()

    def results(self):
        return self._scenario.results()

    def actions(self):
        return self._scenario.actions_executed()

    def calls(self):
        return self._scenario.calls

    def call_count(self):
        return self._scenario.call_count()

    # ---------------------------------------------------------
    # ASSERT HELPERS
    # ---------------------------------------------------------

    async def assert_memory_contains(
        self,
        keywords: list[str],
        *,
        campaign_id: str = "test",
    ):
        memory = await self.memory(campaign_id)

        text = " ".join(memory.recent_events).lower()

        assert any(k.lower() in text for k in keywords), f"Expected one of {keywords} in:\n{text}"

    async def assert_memory_not_empty(self, campaign_id: str = "test"):
        memory = await self.memory(campaign_id)
        events = getattr(memory, "recent_events", []) or []
        assert len(events) > 0, "Expected memory to contain at least one event."

    def assert_last_contains(self, keywords: list[str]):
        last = self.last()
        text = str(last).lower()

        assert any(k.lower() in text for k in keywords), f"Expected one of {keywords} in:\n{text}"

    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------

    def reset(self):
        self._scenario.reset()
