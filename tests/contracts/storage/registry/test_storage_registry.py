import pytest

from semantic_context_server.infrastructure.storage.campaign_storage_factory import _registry


@pytest.mark.contract
def test_all_backends_registered():
    backends = _registry.list()

    assert "json" in backends
    assert "inmemory" in backends
