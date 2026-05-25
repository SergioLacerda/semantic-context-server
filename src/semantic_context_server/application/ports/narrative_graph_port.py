from typing import Any, Protocol


class NarrativeGraphPort(Protocol):
    """
    Port for the Narrative Graph Service, defining the interface for
    managing and querying narrative graph data.
    """

    async def add_node(
        self, campaign_id: str, node_id: str, node_type: str, properties: dict[str, Any]
    ) -> None: ...

    async def add_edge(
        self,
        campaign_id: str,
        source_id: str,
        target_id: str,
        edge_type: str,
        properties: dict[str, Any],
    ) -> None: ...

    async def get_node(self, campaign_id: str, node_id: str) -> dict[str, Any] | None: ...

    async def get_neighbors(
        self, campaign_id: str, node_id: str, edge_type: str | None = None
    ) -> list[dict[str, Any]]: ...

    async def find_path(
        self, campaign_id: str, start_node_id: str, end_node_id: str, max_depth: int = 5
    ) -> list[list[dict[str, Any]]]: ...

    async def query(self, campaign_id: str, query_string: str) -> list[dict[str, Any]]: ...
