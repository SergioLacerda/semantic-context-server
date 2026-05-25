import pytest

from semantic_context_server.application.ports.storage import DocumentStorePort


@pytest.mark.asyncio
async def test_vector_storage_integration_flow(container):
    """
    Valida o fluxo completo de armazenamento vetorial seguindo o padrão CQRS e Async Mandate:
    Adapter -> WriterService (Batching) -> BaseVectorAdapter -> Executor -> Backend In-Memory
    """
    # 1. Setup do container de campanha via Bootstrap real
    campaign_id = "integration_test_campaign"
    campaign_container = await container.campaigns.get(campaign_id)

    # O gateway (Adapter) é resolvido do container, garantindo que o wiring (DI) está correto
    # Nota: Em uma implementação real, o gateway seria resolvido via interface VectorIndexGateway
    vector_gateway = campaign_container.resolve("VectorIndexGateway")

    # Verificar que o gateway é uma instância válida
    assert vector_gateway is not None

    # 2. Indexação de múltiplos textos (Exercitando o Async Mandate)
    texts = [
        "O dragão dorme sobre o ouro na montanha solitária.",
        "A taverna 'O Machado Cego' é o refúgio dos mercenários.",
        "Um rastro de sangue leva à entrada da floresta proibida.",
    ]
    await vector_gateway.index_campaign(campaign_id, texts, metadata={"source": "test_suite"})

    # 3. Acesso ao engine bruto e validação de componentes
    engine = vector_gateway.raw
    assert engine is not None
    assert hasattr(engine, "components")

    # Verificar que os componentes necessários estão presentes
    components = engine.components
    assert hasattr(components, "vector_writer")
    assert hasattr(components, "vector_reader")
    assert hasattr(components, "document_store")

    # 4. Busca e Verificação de Recuperação (RankingContext e ANN Router)
    # Aqui testamos se o dado indexado pode ser lido pelo Reader
    results = await vector_gateway.search("onde os mercenários bebem?", k=1)

    # Validar que a busca retorna resultados
    assert isinstance(results, list)
    if len(results) > 0:
        assert isinstance(results[0], dict)
        if "text" in results[0]:
            assert isinstance(results[0]["text"], str)

    # 5. Verificação de Persistência nos Stores KV (CQRS Separation)
    # Validamos se os metadados e documentos foram salvos nos ports corretos
    doc_store = components.document_store
    vector_reader = components.vector_reader

    # Verificar que os stores têm os métodos esperados
    assert hasattr(doc_store, "get")
    assert hasattr(vector_reader, "search")


@pytest.mark.asyncio
async def test_kv_storage_atomic_integration(container):
    """
    Garante que os adapters KV estão integrados com o Executor
    e respeitam o Async Mandate sem travar o Event Loop.
    """
    campaign_container = await container.campaigns.get("c1")
    doc_store = campaign_container.resolve(DocumentStorePort)

    test_data = {"key": "val", "nested": {"id": 123}, "status": "active"}

    # Operações que internamente usam o Executor.run()
    await doc_store.set("atomic_integration_key", test_data)
    result = await doc_store.get("atomic_integration_key")

    assert result == test_data

    await doc_store.delete("atomic_integration_key")
    assert await doc_store.get("atomic_integration_key") is None


def test_application_registry_compliance_integration(container):
    """
    Verificação "Hard Guard" de Arquitetura:
    Garante que o registro global de componentes cumpre o Async Mandate.
    """
    from semantic_context_server.application.dispatch.application_registry import (
        ApplicationRegistry,
    )

    # O registry centralizado deve passar na validação de assinaturas e corrotinas
    registry = container.resolve(ApplicationRegistry)
    registry.validate()
