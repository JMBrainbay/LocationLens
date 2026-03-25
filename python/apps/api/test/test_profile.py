from fastapi.testclient import TestClient

from app import create_app
from config.env import get_settings
from integrations.types import Building


def test_profile_combines_place_building_metrics() -> None:
    client = TestClient(create_app())
    response = client.get("/api/places/profile?id=adr-damrak-1-amsterdam")
    assert response.status_code == 200
    payload = response.json()
    assert payload["place"]["source"] == "fixture"
    assert payload["building"]["yearBuilt"] == 1912
    assert payload["areaMetrics"]["avgWozX1000Eur"] == 540
    assert payload["sourceBreakdown"]["metrics"] == "fixture"


def test_profile_with_metrics_provider_none(monkeypatch) -> None:
    monkeypatch.setenv("METRICS_PROVIDER", "none")
    get_settings.cache_clear()
    client = TestClient(create_app())
    response = client.get("/api/places/profile?id=adr-damrak-1-amsterdam")
    assert response.status_code == 200
    payload = response.json()
    assert payload["sourceBreakdown"]["metrics"] == "none"


def test_profile_with_bag_provider_success(monkeypatch) -> None:
    from integrations.pdokBag import PdokBagProvider

    async def fake_building_for(self, place):
        return Building(yearBuilt=1998, usageType="woonfunctie", floorAreaM2=92), "bag"

    monkeypatch.setattr(PdokBagProvider, "building_for", fake_building_for)
    monkeypatch.setenv("BUILDING_PROVIDER", "bag")
    get_settings.cache_clear()

    client = TestClient(create_app())
    response = client.get("/api/places/profile?id=adr-damrak-1-amsterdam")
    assert response.status_code == 200
    payload = response.json()
    assert payload["building"]["yearBuilt"] == 1998
    assert payload["sourceBreakdown"]["building"] == "bag"
