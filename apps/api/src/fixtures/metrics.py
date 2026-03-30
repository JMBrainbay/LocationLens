from integrations.types import AreaMetrics

FIXTURE_METRICS_BY_BUURT: dict[str, AreaMetrics] = {
    "BU03630000": AreaMetrics(
        population=12345,
        households=6789,
        housingStock=7100,
        avgWozX1000Eur=540,
        ownerOccupiedPct=42.1,
        rentalPct=57.9,
        densityPerKm2=8200,
        solarPct=11.4,
        gasFreePct=17.8,
    ),
    "BU03440001": AreaMetrics(
        population=8900,
        households=4300,
        housingStock=4600,
        avgWozX1000Eur=410,
        ownerOccupiedPct=36.8,
        rentalPct=63.2,
        densityPerKm2=6500,
        solarPct=9.1,
        gasFreePct=12.5,
    ),
    "BU05990002": AreaMetrics(
        population=15400,
        households=7200,
        housingStock=7500,
        avgWozX1000Eur=320,
        ownerOccupiedPct=28.4,
        rentalPct=71.6,
        densityPerKm2=9900,
        solarPct=6.4,
        gasFreePct=8.3,
    ),
}
