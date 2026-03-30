from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    ok: bool
    service: str
    timestamp: str


@router.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        ok=True,
        service="nl-location-lens-api",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
