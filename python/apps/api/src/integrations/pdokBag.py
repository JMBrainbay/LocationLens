from __future__ import annotations

import httpx

from lib.cache import SimpleTTLCache
from lib.http import get_json
from lib.logger import get_logger
from integrations.types import Building, BuildingSource, ResolvedPlace

logger = get_logger("pdok-bag")


class PdokBagProvider:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.cache = SimpleTTLCache(ttl_seconds=600)
        self.client = httpx.AsyncClient(timeout=7.0)

    async def building_for(self, place: ResolvedPlace) -> tuple[Building, BuildingSource]:
        postal_code = place.address.postalCode if place.address else None
        house_number = place.address.houseNumber if place.address else None
        house_letter = place.address.houseLetter if place.address else None
        house_suffix = place.address.houseNumberSuffix if place.address else None
        if not postal_code or not house_number:
            return Building(), "none"

        # TODO: BAG query params can vary by dataset revision; keep conservative.
        # TODO: Validate if huisletter/huisnummertoevoeging should always be included.
        async def loader() -> tuple[Building, BuildingSource]:
            params: dict[str, str | int] = {"limit": 1, "postcode": postal_code, "huisnummer": house_number}
            if house_letter:
                params["huisletter"] = house_letter
            if house_suffix:
                params["huisnummertoevoeging"] = house_suffix

            payload = await get_json(
                self.client,
                f"{self.base_url}/collections/adressen/items",
                params=params,
            )
            features = payload.get("features")
            if not isinstance(features, list) or not features:
                return Building(), "none"

            properties = features[0].get("properties", {})
            if not isinstance(properties, dict):
                return Building(), "none"
            year_built = properties.get("oorspronkelijkBouwjaar")
            floor_area = properties.get("oppervlakte")
            return (
                Building(
                    yearBuilt=int(year_built) if isinstance(year_built, (int, float)) else None,
                    usageType="unknown",
                    floorAreaM2=int(floor_area) if isinstance(floor_area, (int, float)) else None,
                ),
                "bag",
            )

        try:
            return await self.cache.get_or_set(f"bag:{place.id}", loader)
        except Exception as exc:
            logger.warning("BAG enrichment failed: %s", exc)
            return Building(), "none"
