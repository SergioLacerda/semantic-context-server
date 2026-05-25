class KeyBuilder:
    @staticmethod
    def build(
        *,
        world: str,
        campaign: str,
        domain: str,
        key: str,
    ) -> str:
        return f"{world}:{campaign}:{domain}:{key}"
