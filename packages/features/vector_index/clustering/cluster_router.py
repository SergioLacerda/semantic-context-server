from typing import Protocol, runtime_checkable


@runtime_checkable
class ClusterRouter(Protocol):
    """
    Contrato para roteamento de candidatos baseado em clusters.
    """

    def route(self, candidates: list[str]) -> list[str]: ...
