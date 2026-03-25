import pytest

from config.env import get_settings


@pytest.fixture(autouse=True)
def force_fixture_mode_for_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOCATION_PROVIDER", "fixture")
    monkeypatch.setenv("BUILDING_PROVIDER", "fixture")
    monkeypatch.setenv("METRICS_PROVIDER", "fixture")
    monkeypatch.setenv("CBS_QUERY_STRATEGY", "batch")
    get_settings.cache_clear()
