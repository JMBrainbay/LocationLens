from fastapi import APIRouter, Query, Request

from integrations.types import LocationProfile, SourceBreakdown
from lib.errors import ApiError

router = APIRouter()


@router.get("/api/places/profile", response_model=LocationProfile)
async def profile(request: Request, id: str = Query(..., min_length=1)) -> LocationProfile:
    place_provider = request.app.state.place_provider
    building_provider = request.app.state.building_provider
    metrics_provider = request.app.state.metrics_provider

    place = await place_provider.resolve(id.strip())
    if not place:
        raise ApiError("not_found", f"Place not found for id '{id}'", 404)

    building, building_source = await building_provider.building_for(place)
    metrics, metrics_source = await metrics_provider.metrics_for(place)

    return LocationProfile(
        place=place,
        building=building,
        areaMetrics=metrics,
        sourceBreakdown=SourceBreakdown(
            place=place.source,
            building=building_source,
            metrics=metrics_source,
        ),
    )
