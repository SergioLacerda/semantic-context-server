class DummyLock:
    def __init__(self, locked: bool):
        self._locked = locked

    def locked(self) -> bool:
        return self._locked

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass
