class NarrativeMemory:
    """
    Representa o estado narrativo de uma campanha.

    ✔ Não conhece IO
    ✔ Encapsula comportamento
    ✔ Protege invariantes
    ✔ Expõe API semântica (DDD)
    """

    MAX_RECENT_EVENTS = 50
    MAX_SCENE_STATES = 20
    MAX_WORLD_FACTS = 100

    def __init__(
        self,
        world_facts: list[str] | None = None,
        scene_state: list[str] | None = None,
        recent_events: list[str] | None = None,
        summary: str = "",
    ):
        self._world_facts = list(dict.fromkeys(world_facts or []))
        self._scene_state = list(scene_state or [])
        self._recent_events = list(recent_events or [])
        self._summary = summary or ""

    # ======================================================
    # 🔒 READ API (SEMÂNTICA)
    # ======================================================

    @property
    def summary(self) -> str:
        return self._summary

    @property
    def world_facts(self) -> list[str]:
        return list(self._world_facts)

    @property
    def scene_state(self) -> list[str]:
        return list(self._scene_state)

    @property
    def recent_events(self) -> list[str]:
        return list(self._recent_events)

    # ------------------------------------------------------
    # Semântica de leitura (DDD)
    # ------------------------------------------------------

    def get_recent_events(self, limit: int = 5) -> list[str]:
        return self._recent_events[-limit:]

    def get_scene_snapshot(self, limit: int = 5) -> list[str]:
        return self._scene_state[-limit:]

    def get_world_facts(self, limit: int = 10) -> list[str]:
        return self._world_facts[-limit:]

    def get_summary(self) -> str:
        return self._summary.strip()

    def is_empty(self) -> bool:
        return (
            not self._summary
            and not self._recent_events
            and not self._scene_state
            and not self._world_facts
        )

    # ======================================================
    # 🧠 BEHAVIOR (WRITE)
    # ======================================================

    def add_event(self, text: str) -> None:
        if not text:
            return

        self._recent_events.append(text)
        self._recent_events = self._recent_events[-self.MAX_RECENT_EVENTS :]

    def add_fact(self, fact: str) -> None:
        if not fact:
            return

        if fact not in self._world_facts:
            self._world_facts.append(fact)
            self._world_facts = self._world_facts[-self.MAX_WORLD_FACTS :]

    def update_scene(self, state: str) -> None:
        if not state:
            return

        self._scene_state.append(state)
        self._scene_state = self._scene_state[-self.MAX_SCENE_STATES :]

    def update_summary(self, summary: str) -> None:
        self._summary = (summary or "").strip()

    # ======================================================
    # 🔄 DOMAIN OPERATIONS (NÍVEL MAIS ALTO)
    # ======================================================

    def append_narrative(
        self,
        event: str | None = None,
        scene: str | None = None,
        fact: str | None = None,
        summary: str | None = None,
    ) -> None:
        """
        Atualiza múltiplos aspectos de forma consistente.
        """

        if event:
            self.add_event(event)

        if scene:
            self.update_scene(scene)

        if fact:
            self.add_fact(fact)

        if summary:
            self.update_summary(summary)

    # ======================================================
    # 📦 SERIALIZAÇÃO (BOUNDARY CONTROLADO)
    # ======================================================

    def to_dict(self) -> dict:
        return {
            "world_facts": list(self._world_facts),
            "scene_state": list(self._scene_state),
            "recent_events": list(self._recent_events),
            "summary": self._summary,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NarrativeMemory":
        if not data:
            return cls()

        return cls(
            world_facts=data.get("world_facts"),
            scene_state=data.get("scene_state"),
            recent_events=data.get("recent_events"),
            summary=data.get("summary") or "",
        )
