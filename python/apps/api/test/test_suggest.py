from fastapi.testclient import TestClient

from app import create_app


def test_suggest_short_query_returns_empty() -> None:
    client = TestClient(create_app())
    response = client.get("/api/places/suggest?q=a")
    assert response.status_code == 200
    assert response.json()["results"] == []


def test_suggest_fixture_result() -> None:
    client = TestClient(create_app())
    response = client.get("/api/places/suggest?q=damrak")
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) >= 1
    assert results[0]["source"] == "fixture"
