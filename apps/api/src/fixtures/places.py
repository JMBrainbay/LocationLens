from integrations.types import Address, AreaCodes, ResolvedPlace, SuggestResult

FIXTURE_PLACES: list[ResolvedPlace] = [
    ResolvedPlace(
        id="adr-damrak-1-amsterdam",
        label="Damrak 1, 1012LG Amsterdam",
        type="adres",
        lat=52.3731,
        lon=4.8936,
        address=Address(street="Damrak", houseNumber="1", postalCode="1012LG", city="Amsterdam"),
        areaCodes=AreaCodes(
            buurtCode="BU03630000", wijkCode="WK0363A", gemeenteCode="GM0363"
        ),
        source="fixture",
    ),
    ResolvedPlace(
        id="adr-oudegracht-120-utrecht",
        label="Oudegracht 120, 3511AW Utrecht",
        type="adres",
        lat=52.0909,
        lon=5.1212,
        address=Address(
            street="Oudegracht", houseNumber="120", postalCode="3511AW", city="Utrecht"
        ),
        areaCodes=AreaCodes(
            buurtCode="BU03440001", wijkCode="WK0344A", gemeenteCode="GM0344"
        ),
        source="fixture",
    ),
    ResolvedPlace(
        id="adr-blaak-88-rotterdam",
        label="Blaak 88, 3011TA Rotterdam",
        type="adres",
        lat=51.9204,
        lon=4.4887,
        address=Address(street="Blaak", houseNumber="88", postalCode="3011TA", city="Rotterdam"),
        areaCodes=AreaCodes(
            buurtCode="BU05990002", wijkCode="WK0599B", gemeenteCode="GM0599"
        ),
        source="fixture",
    ),
]

FIXTURE_SUGGESTIONS: list[SuggestResult] = [
    SuggestResult(
        id=place.id,
        label=place.label,
        type=place.type,
        lat=place.lat,
        lon=place.lon,
        source="fixture",
    )
    for place in FIXTURE_PLACES
]
