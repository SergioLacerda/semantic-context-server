from typing import Any


class KVStorageAdapter:
    def __init__(self, campaign_storage_provider: Any) -> None:
        self.provider = campaign_storage_provider

    def get_kv(self, namespace: str) -> Any:
        """
        namespace esperado:
        embedding:campaign:123
        """

        parts = namespace.split(":")

        if len(parts) < 3:
            raise ValueError(f"Invalid namespace: {namespace}")

        _, _, campaign_id = parts[:3]

        storage = self.provider.get(campaign_id)

        return storage.build_kv_store(namespace)
