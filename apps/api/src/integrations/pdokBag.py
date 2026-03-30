from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx

from lib.cache import SimpleTTLCache
from lib.http import get_json
from lib.logger import get_logger
from integrations.types import Building, BuildingSource, ResolvedPlace

logger = get_logger("pdok-bag")


def _to_int(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _to_str(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if isinstance(value, int):
        return str(value)
    return None


def _normalize_postcode(value: str | None) -> str | None:
    if not value:
        return None
    return value.replace(" ", "").upper()


def _normalize_house_number(value: str | None) -> str | None:
    if not value:
        return None
    return str(_to_int(value) if _to_int(value) is not None else value).strip()


def _extract_first_feature(payload: dict[str, Any]) -> dict[str, Any] | None:
    features = payload.get("features")
    if not isinstance(features, list) or not features:
        return None
    feature = features[0]
    if not isinstance(feature, dict):
        return None
    return feature


def _extract_properties(payload: dict[str, Any]) -> dict[str, Any] | None:
    feature = _extract_first_feature(payload)
    if not feature:
        return None
    properties = feature.get("properties")
    if not isinstance(properties, dict):
        return None
    return properties


class PdokBagProvider:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.cache = SimpleTTLCache(ttl_seconds=600)
        self.client = httpx.AsyncClient(timeout=7.0)

    async def _find_address_properties(self, place: ResolvedPlace) -> dict[str, Any] | None:
        if place.lat is None or place.lon is None:
            return None

        target_postcode = _normalize_postcode(place.address.postalCode if place.address else None)
        target_number = _normalize_house_number(place.address.houseNumber if place.address else None)
        target_letter = _to_str(place.address.houseLetter if place.address else None)
        target_suffix = _to_str(place.address.houseNumberSuffix if place.address else None)

        if not target_postcode or not target_number:
            return None

        delta = 0.001
        params: dict[str, str | int] = {
            "limit": 100,
            "bbox": f"{place.lon - delta},{place.lat - delta},{place.lon + delta},{place.lat + delta}",
        }

        for _ in range(10):
            payload = await get_json(
                self.client,
                f"{self.base_url}/collections/adres/items",
                params=params,
            )

            features = payload.get("features")
            if isinstance(features, list):
                for feature in features:
                    if not isinstance(feature, dict):
                        continue
                    properties = feature.get("properties")
                    if not isinstance(properties, dict):
                        continue

                    postcode = _normalize_postcode(_to_str(properties.get("postcode")))
                    house_number = _normalize_house_number(_to_str(properties.get("huisnummer")))
                    house_letter = _to_str(properties.get("huisletter"))
                    house_suffix = _to_str(properties.get("toevoeging"))

                    if postcode != target_postcode or house_number != target_number:
                        continue
                    if target_letter and house_letter and target_letter.upper() != house_letter.upper():
                        continue
                    if target_suffix and house_suffix and target_suffix.upper() != house_suffix.upper():
                        continue
                    return properties

            next_cursor: str | None = None
            links = payload.get("links")
            if isinstance(links, list):
                for link in links:
                    if not isinstance(link, dict):
                        continue
                    if link.get("rel") != "next":
                        continue
                    href = link.get("href")
                    if not isinstance(href, str):
                        continue
                    cursor_values = parse_qs(urlparse(href).query).get("cursor")
                    if cursor_values:
                        next_cursor = cursor_values[0]
                        break
            if not next_cursor:
                break
            params = {"limit": 100, "bbox": params["bbox"], "cursor": next_cursor}

        return None

    async def _fetch_verblijfsobject(self, identificatie: str) -> dict[str, Any] | None:
        payload = await get_json(
            self.client,
            f"{self.base_url}/collections/verblijfsobject/items",
            params={"limit": 1, "identificatie": identificatie},
        )
        return _extract_properties(payload)

    async def _fetch_pand(self, vbo_properties: dict[str, Any]) -> dict[str, Any] | None:
        pand_hrefs = vbo_properties.get("pand.href")
        if isinstance(pand_hrefs, list) and pand_hrefs and isinstance(pand_hrefs[0], str):
            payload = await get_json(self.client, pand_hrefs[0], params=None)
            return _extract_properties(payload)

        pand_ids = vbo_properties.get("pand")
        if isinstance(pand_ids, list) and pand_ids and isinstance(pand_ids[0], str):
            payload = await get_json(
                self.client,
                f"{self.base_url}/collections/pand/items",
                params={"limit": 1, "identificatie": pand_ids[0]},
            )
            return _extract_properties(payload)

        return None

    async def building_for(self, place: ResolvedPlace) -> tuple[Building, BuildingSource]:
        postal_code = _normalize_postcode(place.address.postalCode if place.address else None)
        house_number = _normalize_house_number(place.address.houseNumber if place.address else None)
        if not postal_code or not house_number:
            return Building(), "none"

        # TODO: BAG query params can vary by dataset revision; keep conservative.
        # TODO: Consider direct nummeraanduiding-id joins when PDOK contract exposes these ids.
        async def loader() -> tuple[Building, BuildingSource]:
            address_properties = await self._find_address_properties(place)
            if not address_properties:
                return Building(), "none"

            object_id = _to_str(address_properties.get("adresseerbaar_object_identificatie"))
            if not object_id:
                return Building(), "none"

            vbo_properties = await self._fetch_verblijfsobject(object_id)
            if not vbo_properties:
                return Building(), "none"

            pand_properties = await self._fetch_pand(vbo_properties)

            building = Building(
                yearBuilt=_to_int(pand_properties.get("bouwjaar")) if pand_properties else None,
                usageType=_to_str(vbo_properties.get("gebruiksdoel"))
                or (_to_str(pand_properties.get("gebruiksdoel")) if pand_properties else None),
                floorAreaM2=_to_int(vbo_properties.get("oppervlakte")),
            )

            has_any = any(value is not None for value in building.model_dump().values())
            return (building, "bag") if has_any else (Building(), "none")

        try:
            return await self.cache.get_or_set(f"bag:{place.id}", loader)
        except Exception as exc:
            logger.warning("BAG enrichment failed: %s", exc)
            return Building(), "none"
