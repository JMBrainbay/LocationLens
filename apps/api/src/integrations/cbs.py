from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Literal

import httpx

from lib.cache import SimpleTTLCache
from lib.http import get_json
from lib.logger import get_logger
from integrations.types import AreaMetrics, MetricsSource, ResolvedPlace

logger = get_logger("cbs")

CbsStrategy = Literal["batch", "targeted"]
GetJsonFn = Callable[[httpx.AsyncClient, str, dict[str, Any]], Awaitable[dict[str, Any]]]

# Curated metric mapping for CBS table 86165NED Observations.
# TODO: Validate metric semantics/units against CBS metadata for workshop wording.
METRIC_TO_MEASURE_ID: dict[str, str] = {
    "population": "T001036",
    "households": "1050010_2",
    "housingStock": "M000297",
    "avgWozX1000Eur": "M001642",
    "ownerOccupiedPct": "1014800",
    "rentalPct": "1014850_2",
    "densityPerKm2": "ST0003",
    "solarPct": "M008297",
    "gasFreePct": "M008295",
}


def _extract_numeric_observation_value(observation: dict[str, Any]) -> float | None:
    if observation.get("ValueAttribute") not in (None, "None"):
        return None
    value = observation.get("Value")
    if isinstance(value, (int, float)):
        return float(value)
    return None


def map_observations_to_metrics(observations: list[dict[str, Any]]) -> AreaMetrics:
    by_measure: dict[str, float | None] = {}
    for observation in observations:
        measure_id = observation.get("Measure")
        if not isinstance(measure_id, str):
            continue
        if measure_id not in METRIC_TO_MEASURE_ID.values():
            continue
        by_measure[measure_id] = _extract_numeric_observation_value(observation)

    payload: dict[str, float | None] = {}
    for metric_key, measure_id in METRIC_TO_MEASURE_ID.items():
        payload[metric_key] = by_measure.get(measure_id)

    return AreaMetrics(**payload)


def _has_any_metric(metrics: AreaMetrics) -> bool:
    return any(value is not None for value in metrics.model_dump().values())


class CbsMetricsProvider:
    def __init__(
        self,
        base_url: str,
        table_id: str,
        strategy: CbsStrategy = "batch",
        get_json_fn: GetJsonFn = get_json,
    ):
        self.base_url = base_url.rstrip("/")
        self.table_id = table_id
        self.strategy = strategy
        self.get_json_fn = get_json_fn
        self.cache = SimpleTTLCache(ttl_seconds=600)
        self.client = httpx.AsyncClient(timeout=7.0)

    async def _fetch_batch_metrics(self, buurt_code: str) -> AreaMetrics:
        payload = await self.get_json_fn(
            self.client,
            f"{self.base_url}/{self.table_id}/Observations",
            {
                "$filter": f"WijkenEnBuurten eq '{buurt_code}'",
                "$select": "Measure,Value,ValueAttribute,WijkenEnBuurten",
                "$top": 3000,
            },
        )
        values = payload.get("value")
        if not isinstance(values, list):
            return AreaMetrics()
        observations = [row for row in values if isinstance(row, dict)]
        return map_observations_to_metrics(observations)

    async def _fetch_targeted_metric(self, buurt_code: str, measure_id: str) -> float | None:
        payload = await self.get_json_fn(
            self.client,
            f"{self.base_url}/{self.table_id}/Observations",
            {
                "$filter": f"WijkenEnBuurten eq '{buurt_code}' and Measure eq '{measure_id}'",
                "$select": "Measure,Value,ValueAttribute,WijkenEnBuurten",
                "$top": 1,
            },
        )
        values = payload.get("value")
        if not isinstance(values, list) or not values or not isinstance(values[0], dict):
            return None
        return _extract_numeric_observation_value(values[0])

    async def _fetch_targeted_metrics(self, buurt_code: str) -> AreaMetrics:
        payload: dict[str, float | None] = {}
        for metric_key, measure_id in METRIC_TO_MEASURE_ID.items():
            cache_key = f"cbs:targeted:{buurt_code}:{measure_id}"
            payload[metric_key] = await self.cache.get_or_set(
                cache_key, lambda m=measure_id: self._fetch_targeted_metric(buurt_code, m)
            )
        return AreaMetrics(**payload)

    async def metrics_for(self, place: ResolvedPlace) -> tuple[AreaMetrics, MetricsSource]:
        buurt_code = place.areaCodes.buurtCode if place.areaCodes else None
        if not buurt_code:
            return AreaMetrics(), "none"

        async def loader() -> tuple[AreaMetrics, MetricsSource]:
            if self.strategy == "targeted":
                metrics = await self._fetch_targeted_metrics(buurt_code)
            else:
                metrics = await self._fetch_batch_metrics(buurt_code)
            return (metrics, "cbs") if _has_any_metric(metrics) else (AreaMetrics(), "none")

        try:
            return await self.cache.get_or_set(f"cbs:{self.strategy}:{buurt_code}", loader)
        except Exception as exc:
            logger.warning("CBS metrics failed: %s", exc)
            return AreaMetrics(), "none"
