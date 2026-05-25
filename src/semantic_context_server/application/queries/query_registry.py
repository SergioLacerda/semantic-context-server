class QueryRegistry:
    def __init__(self) -> None:
        self._queries_by_name: dict[str, type] = {}

    # ======================================================
    # REGISTER
    # ======================================================

    def register(self, query_type: type, name: str) -> None:
        key = name.lower()

        if key in self._queries_by_name:
            raise RuntimeError(f"Query already registered: {name}")

        self._queries_by_name[key] = query_type

    # ======================================================
    # RESOLVE
    # ======================================================

    def get(self, name: str) -> type | None:
        if not name:
            return None

        return self._queries_by_name.get(name.lower())

    # ======================================================
    # DEBUG
    # ======================================================

    def list(self) -> list[str]:
        return list(self._queries_by_name.keys())
