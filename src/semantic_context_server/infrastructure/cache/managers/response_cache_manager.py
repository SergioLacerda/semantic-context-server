from typing import Any


class ResponseCacheManager:
    def __init__(self, base_cache_manager: Any) -> None:
        self.base = base_cache_manager

    def get(self, namespace: str) -> Any:
        return self.base.get(f"response:{namespace}")

    def invalidate(self, namespace: str) -> None:
        self.base.invalidate(f"response:{namespace}")
