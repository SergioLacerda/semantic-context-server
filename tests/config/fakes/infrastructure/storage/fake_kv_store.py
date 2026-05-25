class FakeKVStore:
    def __init__(self):
        self._store: dict[str, dict] = {}
        self.calls: list[dict] = []

    # ---------------------------------------------------------

    async def get(self, key: str):
        self.calls.append({"op": "get", "key": key})
        return self._store.get(key)

    async def set(self, key: str, value):
        self.calls.append({"op": "set", "key": key, "value": value})
        self._store[key] = value

    async def delete(self, key: str):
        self.calls.append({"op": "delete", "key": key})
        self._store.pop(key, None)

    async def clear(self):
        self.calls.append({"op": "clear"})
        self._store.clear()
