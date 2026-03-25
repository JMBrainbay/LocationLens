from fastapi.testclient import TestClient

from app import create_app


def test_resolve_fixture_place() -> None:
    client = TestClient(create_app())
    response = client.get("/api/places/resolve?id=adr-damrak-1-amsterdam")
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "adr-damrak-1-amsterdam"
    assert payload["source"] == "fixture"
    assert payload["address"]["postalCode"] == "1012LG"


def test_resolve_missing_place() -> None:
    client = TestClient(create_app())
    response = client.get("/api/places/resolve?id=unknown")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
