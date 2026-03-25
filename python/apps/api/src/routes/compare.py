from fastapi import APIRouter, Query, Request

from integrations.types import CompareDelta, CompareResponse
from lib.errors import ApiError
from routes.places_profile import profile

router = APIRouter()

METRIC_LABELS: dict[str, str] = {
    "population": "Population",
    "households": "Households",
    "housingStock": "Housing stock",
    "avgWozX1000Eur": "Average WOZ (x1000 EUR)",
    "ownerOccupiedPct": "Owner occupied (%)",
    "rentalPct": "Rental (%)",
    "densityPerKm2": "Density per km2",
    "solarPct": "Solar (%)",
    "gasFreePct": "Gas free (%)",
}


@router.get("/api/compare", response_model=CompareResponse)
async def compare(
    request: Request,
    left: str = Query(..., min_length=1),
    right: str = Query(..., min_length=1),
) -> CompareResponse:
    if left == right:
        raise ApiError("invalid_compare", "left and right must differ", 400)

    left_profile = await profile(request, left)
    right_profile = await profile(request, right)

    deltas: list[CompareDelta] = []
    left_metrics = left_profile.areaMetrics.model_dump()
    right_metrics = right_profile.areaMetrics.model_dump()
    for key, label in METRIC_LABELS.items():
        left_value = left_metrics.get(key)
        right_value = right_metrics.get(key)
        if left_value is None or right_value is None:
            continue
        deltas.append(
            CompareDelta(
                key=key,
                label=label,
                left=float(left_value),
                right=float(right_value),
                difference=float(left_value) - float(right_value),
            )
        )

    return CompareResponse(left=left_profile, right=right_profile, deltas=deltas)
