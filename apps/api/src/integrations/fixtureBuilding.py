from fixtures.buildings import FIXTURE_BUILDINGS_BY_PLACE_ID
from integrations.types import Building, BuildingSource, ResolvedPlace


class FixtureBuildingProvider:
    async def building_for(self, place: ResolvedPlace) -> tuple[Building, BuildingSource]:
        building = FIXTURE_BUILDINGS_BY_PLACE_ID.get(place.id)
        if not building:
            return Building(), "none"
        return building, "fixture"
