from integrations.types import Building, BuildingSource, ResolvedPlace


class EpOnlineProvider:
    def __init__(self, enabled: bool):
        self.enabled = enabled

    async def building_for(self, place: ResolvedPlace) -> tuple[Building, BuildingSource]:
        if not self.enabled:
            return Building(), "none"
        # TODO: Wire EP-Online lookup when API details are finalized.
        return Building(), "none"
