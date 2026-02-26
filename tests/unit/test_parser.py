from __future__ import annotations

import pytest

from cellar_wrapper.errors import CellarParseError
from cellar_wrapper.parser import parse_act_refs, parse_bindings, parse_case_law_items
from tests.helpers import sparql_payload, sparql_row


def test_parse_bindings_missing_results_raises() -> None:
    with pytest.raises(CellarParseError):
        parse_bindings({})


def test_parse_act_refs_requires_uri_column() -> None:
    rows = [sparql_row(celex="32022R2554")]
    with pytest.raises(CellarParseError):
        parse_act_refs(rows)


def test_parse_case_law_items_maps_case_fields() -> None:
    rows = [
        sparql_row(
            other="http://publications.europa.eu/resource/cellar/case",
            celex="62019CJ0287",
            ecli="ECLI:EU:C:2020:897",
            courtFormation="Izba I",
        )
    ]
    items = parse_case_law_items(rows)
    assert len(items) == 1
    assert items[0].ecli == "ECLI:EU:C:2020:897"


def test_parse_bindings_reads_expected_structure() -> None:
    payload = sparql_payload([sparql_row(work="http://publications.europa.eu/resource/cellar/work")])
    bindings = parse_bindings(payload)
    assert len(bindings) == 1
