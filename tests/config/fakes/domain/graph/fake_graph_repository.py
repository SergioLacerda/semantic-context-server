from tests.config.fakes.domain.graph.fake_graph import FakeGraph


class FakeGraphRepository:
    """
    Fake de repositório de grafo.

    ✔ compatível com NarrativeGraph
    ✔ funciona com NarrativeGraphService
    ✔ pode retornar FakeGraph ou dados crus
    """

    def __init__(self, graph=None, initial_data=None):
        # usado quando o service usa graph diretamente
        self.graph = graph or FakeGraph()

        # usado quando NarrativeGraph.load() é chamado
        self._data = initial_data or {
            "graph": {},
            "frequency": {},
        }

        self.loaded_campaign = None
        self.saved = None

    # ---------------------------------------------------------
    # LOAD
    # ---------------------------------------------------------

    async def load(self, campaign_id: str):
        self.loaded_campaign = campaign_id
        return self.graph

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    async def save(self, campaign_id: str, data):
        self.saved = (campaign_id, data)
        self.graph = data
