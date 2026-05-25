import time
from collections import OrderedDict
from typing import Any


class CampaignManager:
    def __init__(self, builder: Any, max_size: int = 100, ttl: int = 3600) -> None:
        self.builder = builder
        self.cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl

    async def get(self, campaign_id: str) -> Any:
        now = time.time()

        if campaign_id in self.cache:
            runtime, _ = self.cache[campaign_id]
            self.cache.move_to_end(campaign_id)
            self.cache[campaign_id] = (runtime, now)
            return runtime

        runtime = await self.builder.build_campaign(campaign_id)

        self.cache[campaign_id] = (runtime, now)
        await self._evict(now)

        return runtime

    async def _evict(self, now: float) -> None:
        expired = [cid for cid, (_, ts) in self.cache.items() if now - ts > self.ttl]

        for cid in expired:
            runtime, _ = self.cache.pop(cid)
            await runtime.shutdown()

        while len(self.cache) > self.max_size:
            _, (runtime, _) = self.cache.popitem(last=False)
            await runtime.shutdown()

    async def clear(self, campaign_id: str) -> None:
        if campaign_id in self.cache:
            runtime, _ = self.cache.pop(campaign_id)
            await runtime.shutdown()

    async def shutdown(self) -> None:
        for runtime, _ in self.cache.values():
            await runtime.shutdown()
        self.cache.clear()
