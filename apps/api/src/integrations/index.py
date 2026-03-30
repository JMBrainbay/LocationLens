from config.env import Settings
from integrations.cbs import CbsMetricsProvider
from integrations.epOnline import EpOnlineProvider
from integrations.fixtureBuilding import FixtureBuildingProvider
from integrations.fixtureMetrics import FixtureMetricsProvider
from integrations.fixturePlace import FixturePlaceProvider
from integrations.pdokBag import PdokBagProvider
from integrations.pdokLocatieserver import PdokLocatieserverProvider
from integrations.types import AreaMetrics, Building, MetricsSource, ResolvedPlace


class NoneBuildingProvider:
    async def building_for(self, place: ResolvedPlace) -> tuple[Building, str]:
        return Building(), "none"


class NoneMetricsProvider:
    async def metrics_for(self, place: ResolvedPlace) -> tuple[AreaMetrics, MetricsSource]:
        return AreaMetrics(), "none"


def build_providers(settings: Settings) -> dict[str, object]:
    if settings.LOCATION_PROVIDER in ("pdok", "live"):
        place_provider = PdokLocatieserverProvider(str(settings.PDOK_LOCATIESERVER_BASE_URL))
    else:
        place_provider = FixturePlaceProvider()

    if settings.BUILDING_PROVIDER in ("bag", "live"):
        building_provider: object = PdokBagProvider(str(settings.PDOK_BAG_OGC_BASE_URL))
    elif settings.BUILDING_PROVIDER == "none":
        building_provider = NoneBuildingProvider()
    elif settings.ENABLE_EP_ONLINE:
        building_provider = EpOnlineProvider(settings.ENABLE_EP_ONLINE)
    else:
        building_provider = FixtureBuildingProvider()

    if settings.METRICS_PROVIDER in ("cbs", "live"):
        metrics_provider: object = CbsMetricsProvider(
            str(settings.CBS_ODATA_BASE_URL),
            settings.CBS_TABLE_ID,
            settings.CBS_QUERY_STRATEGY,
        )
    elif settings.METRICS_PROVIDER == "none":
        metrics_provider = NoneMetricsProvider()
    else:
        metrics_provider = FixtureMetricsProvider()

    return {
        "place_provider": place_provider,
        "building_provider": building_provider,
        "metrics_provider": metrics_provider,
    }
