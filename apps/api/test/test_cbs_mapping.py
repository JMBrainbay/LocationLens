import asyncio

from integrations.cbs import CbsMetricsProvider, map_observations_to_metrics
from integrations.types import AreaCodes, ResolvedPlace


def test_cbs_mapping_curated_keys() -> None:
    observations = [
        {"Measure": "T001036", "Value": 1000, "ValueAttribute": "None"},
        {"Measure": "M001642", "Value": 525, "ValueAttribute": "None"},
        {"Measure": "M008295", "Value": 16.4, "ValueAttribute": "None"},
    ]
    metrics = map_observations_to_metrics(observations)
    assert metrics.population == 1000
    assert metrics.avgWozX1000Eur == 525
    assert metrics.gasFreePct == 16.4


def make_place() -> ResolvedPlace:
    return ResolvedPlace(
        id="adr-example",
        label="Example",
        type="adres",
        lat=None,
        lon=None,
        address=None,
        areaCodes=AreaCodes(buurtCode="BU123", wijkCode=None, gemeenteCode=None),
        source="pdok",
    )


def test_cbs_batch_strategy_uses_observations() -> None:
    async def fake_get_json(*args: object) -> dict[str, object]:
        params = args[2] if len(args) > 2 else None
        assert isinstance(params, dict)
        assert "WijkenEnBuurten eq 'BU123'" in str(params.get("$filter"))
        return {
            "value": [
                {"Measure": "T001036", "Value": 2890.0, "ValueAttribute": "None"},
                {"Measure": "M001642", "Value": 488.0, "ValueAttribute": "None"},
            ]
        }

    provider = CbsMetricsProvider(
        "https://datasets.cbs.nl/odata/v1/CBS",
        "86165NED",
        "batch",
        fake_get_json,
    )
    metrics, source = asyncio.run(provider.metrics_for(make_place()))
    assert source == "cbs"
    assert metrics.population == 2890.0
    assert metrics.avgWozX1000Eur == 488.0


def test_cbs_targeted_strategy_uses_measure_filters() -> None:
    async def fake_get_json(*args: object) -> dict[str, object]:
        params = args[2] if len(args) > 2 else None
        assert isinstance(params, dict)
        filter_value = str(params.get("$filter"))
        if "Measure eq 'T001036'" in filter_value:
            return {"value": [{"Measure": "T001036", "Value": 2890.0, "ValueAttribute": "None"}]}
        return {"value": []}

    provider = CbsMetricsProvider(
        "https://datasets.cbs.nl/odata/v1/CBS",
        "86165NED",
        "targeted",
        fake_get_json,
    )
    metrics, source = asyncio.run(provider.metrics_for(make_place()))
    assert source == "cbs"
    assert metrics.population == 2890.0
