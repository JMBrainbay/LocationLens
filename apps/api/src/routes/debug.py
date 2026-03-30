from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from config.env import get_settings

router = APIRouter()


class DebugProvidersResponse(BaseModel):
    mode: str
    providers: dict[str, str]
    env: dict[str, str | bool]


@router.get("/api/debug/providers", response_model=DebugProvidersResponse)
async def debug_providers(request: Request) -> DebugProvidersResponse:
    settings = get_settings()
    return DebugProvidersResponse(
        mode="debug",
        providers={
            "place": type(request.app.state.place_provider).__name__,
            "building": type(request.app.state.building_provider).__name__,
            "metrics": type(request.app.state.metrics_provider).__name__,
        },
        env={
            "LOCATION_PROVIDER": settings.LOCATION_PROVIDER,
            "BUILDING_PROVIDER": settings.BUILDING_PROVIDER,
            "METRICS_PROVIDER": settings.METRICS_PROVIDER,
            "ENABLE_EP_ONLINE": settings.ENABLE_EP_ONLINE,
        },
    )
