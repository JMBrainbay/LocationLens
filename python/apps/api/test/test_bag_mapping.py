import asyncio

import integrations.pdokBag as pdok_bag_module
from integrations.pdokBag import PdokBagProvider
from integrations.types import Address, AreaCodes, ResolvedPlace


def make_place() -> ResolvedPlace:
    return ResolvedPlace(
        id="adr-orchidee",
        label="Orchideestraat 12, 3551GJ Utrecht",
        type="adres",
        lat=52.10221904,
        lon=5.09513668,
        address=Address(
            street="Orchideestraat",
            houseNumber="12",
            houseLetter=None,
            houseNumberSuffix=None,
            postalCode="3551GJ",
            city="Utrecht",
        ),
        areaCodes=AreaCodes(buurtCode="BU03440224", wijkCode="WK034402", gemeenteCode="0344"),
        source="pdok",
    )


def test_bag_provider_maps_vbo_and_pand(monkeypatch) -> None:
    async def fake_get_json(client, url, params=None):
        if "/collections/adres/items" in url:
            assert params is not None and "bbox" in params
            return {
                "features": [
                    {
                        "properties": {
                            "postcode": "3551GJ",
                            "huisnummer": "12",
                            "identificatie": "0344200000065995",
                            "adresseerbaar_object_identificatie": "0344010000148686",
                        }
                    }
                ]
            }
        if "/collections/verblijfsobject/items" in url:
            return {
                "features": [
                    {
                        "properties": {
                            "identificatie": "0344010000148686",
                            "oppervlakte": 118,
                            "gebruiksdoel": "woonfunctie",
                            "pand": ["0344100000155785"],
                        }
                    }
                ]
            }
        if "/collections/pand/items" in url:
            return {"features": [{"properties": {"identificatie": "0344100000155785", "bouwjaar": 1912}}]}
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(pdok_bag_module, "get_json", fake_get_json)
    provider = PdokBagProvider("https://api.pdok.nl/kadaster/bag/ogc/v2")
    building, source = asyncio.run(provider.building_for(make_place()))
    assert source == "bag"
    assert building.yearBuilt == 1912
    assert building.usageType == "woonfunctie"
    assert building.floorAreaM2 == 118


def test_bag_provider_returns_none_without_matching_address(monkeypatch) -> None:
    async def fake_get_json(client, url, params=None):
        if "/collections/adres/items" in url:
            return {"features": []}
        raise AssertionError("Only adres lookup should run when no match exists")

    monkeypatch.setattr(pdok_bag_module, "get_json", fake_get_json)
    provider = PdokBagProvider("https://api.pdok.nl/kadaster/bag/ogc/v2")
    building, source = asyncio.run(provider.building_for(make_place()))
    assert source == "none"
    assert building.yearBuilt is None
    assert building.floorAreaM2 is None
