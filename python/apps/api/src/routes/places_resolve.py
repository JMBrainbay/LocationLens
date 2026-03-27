from fastapi import APIRouter, Query, Request

from integrations.types import ResolvedPlace
from lib.errors import ApiError

router = APIRouter()


@router.get("/api/places/resolve", response_model=ResolvedPlace)
async def resolve(request: Request, id: str = Query(..., min_length=1)) -> ResolvedPlace:
    provider = request.app.state.place_provider
    place = await provider.resolve(id.strip())
    if not place:
        raise ApiError(
            "not_found",
            "No place matches that ID. Copy an ID from /api/places/suggest (fixture mode includes IDs like adr-damrak-1-amsterdam).",
            404,
        )
    return place
