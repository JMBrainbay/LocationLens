from fastapi.testclient import TestClient

from app import create_app


def test_health() -> None:
    client = TestClient(create_app())
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["service"] == "nl-location-lens-api"
    assert isinstance(payload["timestamp"], str)
