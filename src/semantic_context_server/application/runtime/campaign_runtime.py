from typing import Any


class CampaignRuntime:
    """
    Runtime isolado por campanha.
    Serviços já construídos (sem DI interno).
    """

    def __init__(self, campaign_id: str, services: dict[str, Any], root: Any = None):
        self.id = campaign_id
        self.campaign_id = campaign_id
        self._services = services
        self.root = root or self
        self._initialized = False

    def get(self, name: str) -> Any:
        return self._services[name]

    def resolve(self, port: Any) -> Any:
        if isinstance(port, str):
            return self._resolve_by_name(port)
        found = self._resolve_by_type(port)
        if found is not None:
            return found
        storage_result = self._resolve_from_storage(port)
        if storage_result is not None:
            return storage_result
        raise KeyError(f"Dependency not registered: {port}")

    def _resolve_by_name(self, name: str) -> Any:
        if name == "VectorIndexGateway":
            return self._services.get("vector_index")
        if name in self._services:
            return self._services[name]
        raise KeyError(f"Dependency not registered: {name}")

    def _resolve_by_type(self, port: Any) -> Any:
        for instance in self._services.values():
            try:
                if isinstance(instance, port):
                    return instance
            except TypeError:
                pass
        return None

    def _resolve_from_storage(self, port: Any) -> Any:
        storage = self._services.get("storage")
        if storage is None:
            return None
        builders = {
            "DocumentStorePort": storage.build_document_store,
            "VectorStorePort": storage.build_vector_store,
            "MetadataStorePort": storage.build_metadata_store,
            "TokenStorePort": storage.build_token_store,
        }
        builder = builders.get(getattr(port, "__name__", ""))
        return builder() if builder else None

    def __getattr__(self, name: str) -> Any:
        if name in self._services:
            return self._services[name]

        aliases = {
            "memory_service": "memory",
        }
        mapped = aliases.get(name)
        if mapped and mapped in self._services:
            return self._services[mapped]

        raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")

    def __dir__(self) -> list[str]:
        aliases = {"memory_service"}
        return sorted(set(super().__dir__()) | set(self._services.keys()) | aliases)

    @property
    def memory(self) -> Any:
        return self._services["memory"]

    @property
    def narrative(self) -> Any:
        return self._services["narrative"]

    async def initialize(self) -> None:
        if self._initialized:
            return
        self._initialized = True

    async def shutdown(self) -> None:
        for svc in self._services.values():
            if hasattr(svc, "shutdown"):
                await svc.shutdown()
