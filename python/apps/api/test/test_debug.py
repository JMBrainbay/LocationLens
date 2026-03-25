from fastapi.testclient import TestClient

from app import create_app


def test_debug_providers_endpoint() -> None:
    client = TestClient(create_app())
    response = client.get("/api/debug/providers")
    assert response.status_code == 200
    payload = response.json()

    assert payload["providers"]["place"] == "FixturePlaceProvider"
    assert payload["providers"]["building"] == "FixtureBuildingProvider"
    assert payload["providers"]["metrics"] == "FixtureMetricsProvider"
    assert payload["env"]["LOCATION_PROVIDER"] == "fixture"
