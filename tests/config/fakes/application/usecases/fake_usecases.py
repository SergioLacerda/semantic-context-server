from semantic_context_server.application.contracts.response import Response


class DummyNarrative:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    async def execute(self, *args, **kwargs):
        if self.error:
            raise self.error

        return Response(
            text=self.result or "",
            type="narrative",
            metadata={},
        )


class DummyRoll:
    def __init__(self, result="roll", error=None):
        self.result = result
        self.error = error

    async def execute(self, *args, **kwargs):
        if self.error:
            raise self.error

        if not self.result:
            return None

        return self.result


class DummyEndSession:
    def __init__(self, result="Resumo"):
        self.result = result

    async def execute(self, campaign_id):
        return self.result


class DummyNarrativeUsecase:
    async def execute(self, *args, **kwargs):
        return "narrative"


class DummyRollUsecase:
    async def execute(self, *args, **kwargs):
        return "roll"


class DummyEndSessionUsecase:
    async def execute(self, *args, **kwargs):
        return None


class DummyUsecases:
    def __init__(self):
        self.narrative = DummyNarrativeUsecase()
        self.roll_dice = DummyRollUsecase()
        self.end_session = DummyEndSessionUsecase()
