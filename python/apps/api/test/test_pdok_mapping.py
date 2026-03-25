from integrations.pdokLocatieserver import _map_doc_to_resolved, _map_doc_to_suggest


def test_pdok_suggest_maps_coordinates_from_centroide_ll() -> None:
    doc = {
        "id": "adr-example",
        "weergavenaam": "Example 1, 1234AB Utrecht",
        "centroide_ll": "POINT(5.1212 52.0907)",
    }
    mapped = _map_doc_to_suggest(doc)
    assert mapped.id == "adr-example"
    assert mapped.lat == 52.0907
    assert mapped.lon == 5.1212


def test_pdok_resolve_maps_address_suffix_fields() -> None:
    doc = {
        "weergavenaam": "Example 1A bis, 1234AB Utrecht",
        "straatnaam": "Example",
        "huisnummer": "1",
        "huisletter": "A",
        "huisnummertoevoeging": "bis",
        "postcode": "1234AB",
        "woonplaatsnaam": "Utrecht",
        "buurtcode": "BU123",
        "wijkcode": "WK123",
        "gemeentecode": "GM123",
    }
    mapped = _map_doc_to_resolved(doc, "adr-example")
    assert mapped.address is not None
    assert mapped.address.houseLetter == "A"
    assert mapped.address.houseNumberSuffix == "bis"


def test_pdok_resolve_accepts_numeric_house_number() -> None:
    doc = {
        "weergavenaam": "Orchideestraat 12, 3551GJ Utrecht",
        "straatnaam": "Orchideestraat",
        "huisnummer": 12,
        "postcode": "3551GJ",
        "woonplaatsnaam": "Utrecht",
    }
    mapped = _map_doc_to_resolved(doc, "adr-example")
    assert mapped.address is not None
    assert mapped.address.houseNumber == "12"


def test_pdok_resolve_falls_back_to_house_number_from_label() -> None:
    doc = {
        "weergavenaam": "Orchideestraat 12, 3551GJ Utrecht",
        "straatnaam": "Orchideestraat",
        "postcode": "3551GJ",
        "woonplaatsnaam": "Utrecht",
    }
    mapped = _map_doc_to_resolved(doc, "adr-example")
    assert mapped.address is not None
    assert mapped.address.houseNumber == "12"
