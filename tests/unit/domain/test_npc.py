import pytest

from semantic_context_server.domain.npc.generator import GenerateNPCUseCase


@pytest.fixture
def usecase():
    return GenerateNPCUseCase()


def test_generate_npc_structure(usecase):
    result = usecase.execute("mercador")

    assert isinstance(result, dict)
    assert set(result.keys()) == {"name", "description", "trait"}


def test_generate_npc_description(usecase):
    desc = "mercador sombrio"

    result = usecase.execute(desc)

    assert result["description"] == desc


def test_generate_npc_name_valid(usecase):
    result = usecase.execute("npc")

    assert result["name"] in ["Arkan", "Velra", "Doran", "Selith"]


def test_generate_npc_trait_valid(usecase):
    result = usecase.execute("npc")

    assert result["trait"] in ["frio", "calculista", "irônico"]


def test_generate_npc_deterministic(usecase, monkeypatch):
    def fake_choice(seq):
        return seq[0]

    monkeypatch.setattr("semantic_context_server.domain.npc.generator.random.choice", fake_choice)

    result = usecase.execute("teste")

    assert result["name"] == "Arkan"
    assert result["trait"] == "frio"
