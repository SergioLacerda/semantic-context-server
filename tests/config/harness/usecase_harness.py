from .base import BaseHarness


class UsecaseHarness(BaseHarness):
    def __init__(self, name, *, container_factory, **overrides):
        super().__init__()

        self.name = name
        self.container = container_factory(**overrides)
        self.usecase = getattr(self.container, name)

        assert hasattr(self.usecase, "execute")

    async def run(self, **kwargs):
        result = await self.usecase.execute(**kwargs)

        self.record(input=kwargs, result=result)

        return result
