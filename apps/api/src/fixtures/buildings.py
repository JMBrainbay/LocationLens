from integrations.types import Building

FIXTURE_BUILDINGS_BY_PLACE_ID: dict[str, Building] = {
    "adr-damrak-1-amsterdam": Building(yearBuilt=1912, usageType="residential", floorAreaM2=118),
    "adr-oudegracht-120-utrecht": Building(yearBuilt=1891, usageType="mixed-use", floorAreaM2=96),
    "adr-blaak-88-rotterdam": Building(yearBuilt=2008, usageType="apartment", floorAreaM2=84),
}
