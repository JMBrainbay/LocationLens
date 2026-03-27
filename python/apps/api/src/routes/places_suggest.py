from fastapi import APIRouter, Query, Request

from integrations.types import SuggestResponse
from lib.errors import ApiError

router = APIRouter()


@router.get("/api/places/suggest", response_model=SuggestResponse)
async def suggest(request: Request, q: str = Query(default="", description="Search query")) -> SuggestResponse:
    if len(q.strip()) < 2:
        return SuggestResponse(query=q, results=[])
    if len(q) > 200:
        raise ApiError("invalid_query", "Search text is too long (max 200 characters).", 400)

    provider = request.app.state.place_provider
    results = await provider.suggest(q.strip())
    return SuggestResponse(query=q, results=results)
