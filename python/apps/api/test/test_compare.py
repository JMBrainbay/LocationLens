from fastapi.testclient import TestClient

from app import create_app


def test_compare_returns_deltas() -> None:
    client = TestClient(create_app())
    response = client.get(
        "/api/compare?left=adr-damrak-1-amsterdam&right=adr-oudegracht-120-utrecht"
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["left"]["place"]["id"] == "adr-damrak-1-amsterdam"
    assert payload["right"]["place"]["id"] == "adr-oudegracht-120-utrecht"
    assert len(payload["deltas"]) > 0


def test_compare_same_ids_invalid() -> None:
    client = TestClient(create_app())
    response = client.get("/api/compare?left=adr-damrak-1-amsterdam&right=adr-damrak-1-amsterdam")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_compare"
