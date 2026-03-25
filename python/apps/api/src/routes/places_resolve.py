from fastapi import APIRouter, Query, Request

from integrations.types import ResolvedPlace
from lib.errors import ApiError

router = APIRouter()


@router.get("/api/places/resolve", response_model=ResolvedPlace)
async def resolve(request: Request, id: str = Query(..., min_length=1)) -> ResolvedPlace:
    provider = request.app.state.place_provider
    place = await provider.resolve(id.strip())
    if not place:
        raise ApiError("not_found", f"Place not found for id '{id}'", 404)
    return place
