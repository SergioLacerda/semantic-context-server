from typing import Any


class ListCampaignsQuery:
    """
    Query = leitura pura
    """

    pass


class ListCampaignsQueryHandler:
    def __init__(self, list_campaigns_use_case: Any, cache: Any) -> None:
        self.list_campaigns = list_campaigns_use_case
        self.cache = cache

    async def handle(self, query: Any, ctx: Any = None) -> str:
        cache_key = "campaigns:list"

        cached = await self.cache.get(cache_key)
        if cached:
            return str(cached)

        campaigns = await self.list_campaigns.execute()

        if not campaigns:
            result = "📭 Nenhuma campanha encontrada."
            await self.cache.set(cache_key, result)
            return result

        result = "📚 Campanhas:\n" + "\n".join(campaigns)

        await self.cache.set(cache_key, result)

        return result
