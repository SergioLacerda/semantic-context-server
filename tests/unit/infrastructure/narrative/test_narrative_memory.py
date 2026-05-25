from semantic_context_server.domain.narrative.narrative_memory import NarrativeMemory

# ==========================================================
# INITIAL STATE
# ==========================================================


def test_initial_state():
    mem = NarrativeMemory()

    assert mem.world_facts == []
    assert mem.scene_state == []
    assert mem.recent_events == []
    assert mem.summary == ""
    assert mem.is_empty()


# ==========================================================
# EVENTS
# ==========================================================


def test_add_event():
    mem = NarrativeMemory()

    mem.add_event("dragon appeared")

    assert mem.recent_events == ["dragon appeared"]


def test_add_event_ignores_empty():
    mem = NarrativeMemory()

    mem.add_event("")
    mem.add_event(None)

    assert mem.recent_events == []


def test_add_event_limit():
    mem = NarrativeMemory()

    for i in range(100):
        mem.add_event(str(i))

    assert len(mem.recent_events) <= mem.MAX_RECENT_EVENTS


# ==========================================================
# SUMMARY
# ==========================================================


def test_update_summary():
    mem = NarrativeMemory()

    mem.update_summary("battle ended")

    assert mem.summary == "battle ended"


def test_update_summary_none_resets():
    mem = NarrativeMemory()

    mem.update_summary("something")
    mem.update_summary(None)

    assert mem.summary == ""


# ==========================================================
# WORLD FACTS
# ==========================================================


def test_add_fact():
    mem = NarrativeMemory()

    mem.add_fact("dragons exist")

    assert mem.world_facts == ["dragons exist"]


def test_add_fact_no_duplicates():
    mem = NarrativeMemory()

    mem.add_fact("dragons exist")
    mem.add_fact("dragons exist")

    assert mem.world_facts == ["dragons exist"]


# ==========================================================
# SCENE STATE
# ==========================================================


def test_update_scene():
    mem = NarrativeMemory()

    mem.update_scene("door is open")

    assert mem.scene_state == ["door is open"]


def test_update_scene_limit():
    mem = NarrativeMemory()

    for i in range(50):
        mem.update_scene(str(i))

    assert len(mem.scene_state) <= mem.MAX_SCENE_STATES


# ==========================================================
# DOMAIN OPERATION
# ==========================================================


def test_append_narrative():
    mem = NarrativeMemory()

    mem.append_narrative(
        event="event",
        scene="scene",
        fact="fact",
        summary="summary",
    )

    assert mem.recent_events == ["event"]
    assert mem.scene_state == ["scene"]
    assert mem.world_facts == ["fact"]
    assert mem.summary == "summary"


# ==========================================================
# SERIALIZATION
# ==========================================================


def test_to_dict():
    mem = NarrativeMemory()

    mem.add_event("event1")
    mem.add_fact("fact1")
    mem.update_scene("scene1")
    mem.update_summary("summary")

    data = mem.to_dict()

    assert data["recent_events"] == ["event1"]
    assert data["world_facts"] == ["fact1"]
    assert data["scene_state"] == ["scene1"]
    assert data["summary"] == "summary"


def test_from_dict():
    data = {
        "recent_events": ["event1"],
        "world_facts": ["fact1"],
        "scene_state": ["scene1"],
        "summary": "summary",
    }

    mem = NarrativeMemory.from_dict(data)

    assert mem.recent_events == ["event1"]
    assert mem.world_facts == ["fact1"]
    assert mem.scene_state == ["scene1"]
    assert mem.summary == "summary"


def test_from_dict_empty():
    mem = NarrativeMemory.from_dict(None)

    assert mem.is_empty()
