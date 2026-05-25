from collections.abc import Callable
from typing import Any

from tests.config.fakes.infrastructure.llm.fake_llm_service import FakeLLMService
from tests.config.fakes.infrastructure.vector.fake_vector_index import FakeVectorIndex
from tests.config.harness.campaign_harness import CampaignHarness


class NarrativeHarness(CampaignHarness):
    def __init__(self, *, llm_result: str = "ok"):
        super().__init__()

        self.llm = FakeLLMService(result=llm_result)
        self.vector_index = FakeVectorIndex()

        self._root_container: Any | None = None
        self._scoped: Any | None = None

    @property
    def records(self):
        return self.calls

    def _ensure_scoped(self, container_factory: Callable[..., Any]):
        if self._root_container is None:
            self._root_container = container_factory(
                campaign_id="__init__",
                llm=self.llm,
                vector_index=self.vector_index,
            )

            self._scoped = self._root_container.campaigns

            if self._scoped is None:
                raise RuntimeError("CampaignScopedContainer not initialized")

    async def _get_campaign_container(
        self,
        *,
        container_factory: Callable[..., Any],
        campaign_id: str,
    ):
        self._ensure_scoped(container_factory)

        assert self._scoped is not None

        container = self._scoped.get(campaign_id)

        # ✔ Handle async get() - CampaignScopedContainer.get is async
        if hasattr(container, "__await__"):
            container = await container

        if container is None:
            raise RuntimeError(f"Campaign container not found: {campaign_id}")

        return container

    async def _setup_harness(
        self,
        *,
        container_factory: Callable[..., Any],
        campaign_id: str,
    ):
        """Setup harness and return campaign container"""
        container = await self._get_campaign_container(
            container_factory=container_factory,
            campaign_id=campaign_id,
        )
        return container

    async def run(
        self,
        *,
        container_factory: Callable[..., Any],
        action: str = "look",
        campaign_id: str = "test",
        user_id: str = "u1",
    ):
        container = await self._get_campaign_container(
            container_factory=container_factory,
            campaign_id=campaign_id,
        )

        result = await container.root.narrative.execute(
            campaign_id=campaign_id,
            action=action,
            user_id=user_id,
        )

        self.record_call(
            campaign_id=campaign_id,
            action=action,
            user_id=user_id,
            result=result,
        )

        return result
