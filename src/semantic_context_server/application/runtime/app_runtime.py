from typing import Any


class AppRuntime:
    def __init__(self, container: Any, campaign_manager: Any) -> None:
        self.container = container
        self.campaigns = campaign_manager

    async def shutdown(self) -> None:
        await self.campaigns.shutdown()
