from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve()
while PROJECT_ROOT != PROJECT_ROOT.parent and not (PROJECT_ROOT / "pyproject.toml").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.features.storage import (  # noqa: E402
    CampaignStorageService,
    LegacyCampaignStorageFactory,
)


class FakeFactory:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def build(self, campaign_id: str):
        self.calls.append(campaign_id)
        return {"campaign_id": campaign_id}


def test_storage_service_caches_by_campaign() -> None:
    factory = FakeFactory()
    svc = CampaignStorageService(factory)

    c1_first = svc.get("c1")
    c1_second = svc.get("c1")
    c2 = svc.get("c2")

    assert c1_first is c1_second
    assert c1_first["campaign_id"] == "c1"
    assert c2["campaign_id"] == "c2"
    assert factory.calls == ["c1", "c2"]


def test_storage_service_clear_and_clear_all() -> None:
    factory = FakeFactory()
    svc = CampaignStorageService(factory)

    first = svc.get("c1")
    svc.clear("c1")
    second = svc.get("c1")

    assert first is not second

    svc.get("c2")
    svc.clear_all()
    third = svc.get("c1")

    assert second is not third


def test_legacy_campaign_storage_factory_delegates_builder(monkeypatch) -> None:
    calls: list[tuple[str, str, str]] = []

    def fake_build_campaign_storage(config, campaign_id, executor):
        calls.append((str(config), campaign_id, str(executor)))
        return {"campaign_id": campaign_id}

    monkeypatch.setattr(
        "semantic_context_server.infrastructure.storage.campaign_storage_factory.build_campaign_storage",
        fake_build_campaign_storage,
    )

    factory = LegacyCampaignStorageFactory(config="cfg", executor="exe")
    out = factory.build("c1")

    assert out == {"campaign_id": "c1"}
    assert calls == [("cfg", "c1", "exe")]
