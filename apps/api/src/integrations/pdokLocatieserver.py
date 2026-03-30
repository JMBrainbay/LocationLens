from __future__ import annotations

import re
from typing import Any

import httpx

from lib.cache import SimpleTTLCache
from lib.http import get_json
from lib.logger import get_logger
from integrations.types import Address, AreaCodes, ResolvedPlace, SuggestResult

logger = get_logger("pdok-locatieserver")


def _extract_docs(payload: dict[str, Any]) -> list[dict[str, Any]]:
    response = payload.get("response")
    if isinstance(response, dict):
        docs = response.get("docs")
        if isinstance(docs, list):
            return [doc for doc in docs if isinstance(doc, dict)]
    return []


def _first_str(doc: dict[str, Any], key: str) -> str | None:
    value = doc.get(key)
    if isinstance(value, list) and value:
        value = value[0]
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else str(value)
    return None


def _extract_lat_lon(doc: dict[str, Any]) -> tuple[float | None, float | None]:
    # PDOK often returns WGS84 point text like "POINT(lon lat)" in centroide_ll.
    point_text = _first_str(doc, "centroide_ll")
    if point_text:
        match = re.search(r"POINT\(([-\d.]+)\s+([-\d.]+)\)", point_text)
        if match:
            return float(match.group(2)), float(match.group(1))

    lat_raw = doc.get("lat")
    lon_raw = doc.get("lon")
    if isinstance(lat_raw, (int, float)) and isinstance(lon_raw, (int, float)):
        return float(lat_raw), float(lon_raw)
    return None, None


def _extract_house_number_from_label(label: str) -> str | None:
    # Expected examples: "Orchideestraat 12, 3551GJ Utrecht", "Example 1A bis, 1234AB Utrecht"
    first_segment = label.split(",")[0].strip()
    match = re.search(r"(\d+)\s*(?:[A-Za-z])?(?:\s+\S+)?$", first_segment)
    if not match:
        return None
    return match.group(1)


def _map_doc_to_suggest(doc: dict[str, Any]) -> SuggestResult:
    lat, lon = _extract_lat_lon(doc)
    return SuggestResult(
        id=_first_str(doc, "id") or _first_str(doc, "identificatie") or "unknown",
        label=_first_str(doc, "weergavenaam") or _first_str(doc, "omschrijving") or "Unknown",
        type="adres",
        lat=lat,
        lon=lon,
        source="pdok",
    )


def _map_doc_to_resolved(doc: dict[str, Any], place_id: str) -> ResolvedPlace:
    lat, lon = _extract_lat_lon(doc)
    label = _first_str(doc, "weergavenaam") or "Unknown"
    house_number = _first_str(doc, "huisnummer") or _extract_house_number_from_label(label)
    return ResolvedPlace(
        id=place_id,
        label=label,
        type="adres",
        lat=lat,
        lon=lon,
        address=Address(
            street=_first_str(doc, "straatnaam"),
            houseNumber=house_number,
            houseLetter=_first_str(doc, "huisletter"),
            houseNumberSuffix=_first_str(doc, "huisnummertoevoeging"),
            postalCode=_first_str(doc, "postcode"),
            city=_first_str(doc, "woonplaatsnaam"),
        ),
        areaCodes=AreaCodes(
            buurtCode=_first_str(doc, "buurtcode"),
            wijkCode=_first_str(doc, "wijkcode"),
            gemeenteCode=_first_str(doc, "gemeentecode"),
        ),
        source="pdok",
    )


class PdokLocatieserverProvider:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.cache = SimpleTTLCache(ttl_seconds=300)
        self.client = httpx.AsyncClient(timeout=7.0)

    async def suggest(self, query: str) -> list[SuggestResult]:
        async def loader() -> list[SuggestResult]:
            payload = await get_json(
                self.client,
                f"{self.base_url}/suggest",
                params={"q": query, "rows": 8, "fq": "type:adres"},
            )
            return [_map_doc_to_suggest(doc) for doc in _extract_docs(payload)]

        try:
            return await self.cache.get_or_set(f"suggest:{query.lower()}", loader)
        except Exception as exc:
            logger.warning("PDOK suggest failed: %s", exc)
            return []

    async def resolve(self, place_id: str) -> ResolvedPlace | None:
        async def loader() -> ResolvedPlace | None:
            payload = await get_json(self.client, f"{self.base_url}/lookup", params={"id": place_id})
            docs = _extract_docs(payload)
            if not docs:
                return None
            return _map_doc_to_resolved(docs[0], place_id)

        try:
            return await self.cache.get_or_set(f"lookup:{place_id}", loader)
        except Exception as exc:
            logger.warning("PDOK lookup failed: %s", exc)
            return None
