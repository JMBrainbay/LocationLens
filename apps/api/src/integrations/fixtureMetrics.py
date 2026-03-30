from fixtures.metrics import FIXTURE_METRICS_BY_BUURT
from integrations.types import AreaMetrics, MetricsSource, ResolvedPlace


class FixtureMetricsProvider:
    async def metrics_for(self, place: ResolvedPlace) -> tuple[AreaMetrics, MetricsSource]:
        buurt_code = place.areaCodes.buurtCode if place.areaCodes else None
        if not buurt_code:
            return AreaMetrics(), "none"
        metrics = FIXTURE_METRICS_BY_BUURT.get(buurt_code)
        if not metrics:
            return AreaMetrics(), "none"
        return metrics, "fixture"
