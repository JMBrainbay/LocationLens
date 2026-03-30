from __future__ import annotations

from fixtures.places import FIXTURE_PLACES, FIXTURE_SUGGESTIONS
from integrations.types import ResolvedPlace, SuggestResult


class FixturePlaceProvider:
    async def suggest(self, query: str) -> list[SuggestResult]:
        q = query.strip().lower()
        return [item for item in FIXTURE_SUGGESTIONS if q in item.label.lower()]

    async def resolve(self, place_id: str) -> ResolvedPlace | None:
        for place in FIXTURE_PLACES:
            if place.id == place_id:
                return place
        return None
