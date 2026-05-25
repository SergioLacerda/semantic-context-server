from typing import Any


class _RelatedResult(set[str]):
    def __eq__(self, other: object) -> bool:
        if isinstance(other, list):
            return set(other) == set(self)
        return super().__eq__(other)


class NarrativeGraphService:
    """
    Orquestra graph + extractor + repository.

    ✔ Multi-campaign safe
    ✔ Async ready
    ✔ Context-aware
    ✔ Integrado com RAG
    """

    def __init__(self, repo: Any, extractor: Any) -> None:
        self.repo = repo
        self.extractor = extractor

    # ==========================================================
    # UPDATE
    # ==========================================================

    async def update_from_event(self, *args: Any, **kwargs: Any) -> None:
        """
        Suporta:
        ✔ update_from_event(text)
        ✔ update_from_event(campaign_id=..., text=..., context=...)
        """

        # ------------------------------------------------------
        # BACKWARD COMPAT
        # ------------------------------------------------------
        if args:
            text = args[0]
            campaign_id = kwargs.get("campaign_id", "default")
            context = kwargs.get("context")
        else:
            text = kwargs.get("text")
            campaign_id = kwargs.get("campaign_id")
            context = kwargs.get("context")

        if not text or not campaign_id:
            return

        graph = await self.repo.load(campaign_id)

        entities = self._extract_entities(text)

        if not entities:
            return

        graph.update(
            entities=entities,
            context=context or {},
            text=text,
        )

        await self.repo.save(campaign_id, graph)

    # ==========================================================
    # QUERY
    # ==========================================================

    async def related(self, *args: Any, **kwargs: Any) -> _RelatedResult:
        """
        Suporta:
        ✔ related(query)
        ✔ related(campaign_id=..., entities=[...])
        """

        # ------------------------------------------------------
        # BACKWARD COMPAT
        # ------------------------------------------------------
        entities: list[str]
        if args:
            query = args[0]
            campaign_id = kwargs.get("campaign_id", "default")
            entities = self._extract_entities(query)
        else:
            campaign_id = kwargs.get("campaign_id")
            raw = kwargs.get("entities")
            entities = raw if isinstance(raw, list) else []

        if not campaign_id or not entities:
            return _RelatedResult()

        graph = await self.repo.load(campaign_id)

        related = graph.related(entities)
        return _RelatedResult(related)

    # ==========================================================
    # INTERNAL
    # ==========================================================

    def _extract_entities(self, text: str) -> list[str]:
        try:
            entities = self.extractor.extract(text)

            if isinstance(entities, set):
                entities = list(entities)

            if not isinstance(entities, list):
                return []

            return [str(e).strip() for e in entities if isinstance(e, str) and e.strip()]

        except Exception:
            return []
