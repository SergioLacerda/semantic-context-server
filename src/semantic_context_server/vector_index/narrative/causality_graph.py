from collections import defaultdict
from collections.abc import Iterable


class CausalityGraph:
    """
    Grafo causal simples entre documentos.

    doc A → doc B (A influencia B)
    """

    def __init__(self) -> None:
        self.forward: dict[str, list[str]] = defaultdict(list)  # A -> [B, C]
        self.backward: dict[str, list[str]] = defaultdict(list)  # B -> [A]

    # ---------------------------------------------------------
    # adicionar relação
    # ---------------------------------------------------------

    def add_edge(self, source: str, target: str) -> None:
        self.forward[source].append(target)
        self.backward[target].append(source)

    # ---------------------------------------------------------
    # expansão causal
    # ---------------------------------------------------------

    def expand(self, doc_ids: Iterable[str], depth: int = 2) -> list[str]:
        visited: set[str] = set(doc_ids)
        frontier: set[str] = set(visited)

        for _ in range(depth):
            new_nodes: set[str] = set()

            for doc_id in frontier:
                # forward
                for nxt in self.forward.get(doc_id, []):
                    if nxt not in visited:
                        new_nodes.add(nxt)

                # backward
                for prev in self.backward.get(doc_id, []):
                    if prev not in visited:
                        new_nodes.add(prev)

            visited.update(new_nodes)
            frontier = new_nodes

        return list(visited)
