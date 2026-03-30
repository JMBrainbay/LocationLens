from __future__ import annotations

from typing import Literal, Protocol

from pydantic import BaseModel


PlaceSource = Literal["fixture", "pdok"]
BuildingSource = Literal["fixture", "bag", "none"]
MetricsSource = Literal["fixture", "cbs", "none"]
PlaceType = Literal["adres", "pand", "wijk", "gemeente", "unknown"]


class Address(BaseModel):
    street: str | None = None
    houseNumber: str | None = None
    houseLetter: str | None = None
    houseNumberSuffix: str | None = None
    postalCode: str | None = None
    city: str | None = None


class AreaCodes(BaseModel):
    buurtCode: str | None = None
    wijkCode: str | None = None
    gemeenteCode: str | None = None


class SuggestResult(BaseModel):
    id: str
    label: str
    type: PlaceType = "unknown"
    lat: float | None = None
    lon: float | None = None
    source: PlaceSource


class SuggestResponse(BaseModel):
    query: str
    results: list[SuggestResult]


class ResolvedPlace(BaseModel):
    id: str
    label: str
    type: PlaceType = "unknown"
    lat: float | None = None
    lon: float | None = None
    address: Address | None = None
    areaCodes: AreaCodes | None = None
    source: PlaceSource


class Building(BaseModel):
    yearBuilt: int | None = None
    usageType: str | None = None
    floorAreaM2: int | None = None


class AreaMetrics(BaseModel):
    population: float | None = None
    households: float | None = None
    housingStock: float | None = None
    avgWozX1000Eur: float | None = None
    ownerOccupiedPct: float | None = None
    rentalPct: float | None = None
    densityPerKm2: float | None = None
    solarPct: float | None = None
    gasFreePct: float | None = None


class SourceBreakdown(BaseModel):
    place: PlaceSource
    building: BuildingSource
    metrics: MetricsSource


class LocationProfile(BaseModel):
    place: ResolvedPlace
    building: Building
    areaMetrics: AreaMetrics
    sourceBreakdown: SourceBreakdown


class CompareDelta(BaseModel):
    key: str
    label: str
    left: float
    right: float
    difference: float


class CompareResponse(BaseModel):
    left: LocationProfile
    right: LocationProfile
    deltas: list[CompareDelta]


class PlaceProvider(Protocol):
    async def suggest(self, query: str) -> list[SuggestResult]: ...

    async def resolve(self, place_id: str) -> ResolvedPlace | None: ...


class BuildingProvider(Protocol):
    async def building_for(self, place: ResolvedPlace) -> tuple[Building, BuildingSource]: ...


class MetricsProvider(Protocol):
    async def metrics_for(self, place: ResolvedPlace) -> tuple[AreaMetrics, MetricsSource]: ...
