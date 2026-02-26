from __future__ import annotations

import pytest

from cellar_wrapper.errors import CellarParseError
from cellar_wrapper.parser import (
    parse_act_detail,
    parse_act_refs,
    parse_bindings,
    parse_case_law_items,
)
from tests.helpers import sparql_payload, sparql_row


def test_parse_bindings_missing_results_raises() -> None:
    with pytest.raises(CellarParseError) as exc_info:
        parse_bindings({})

    assert exc_info.value.details["parser"] == "parse_bindings"
    assert exc_info.value.details["field"] == "results.bindings"


def test_parse_act_refs_requires_uri_column() -> None:
    rows = [sparql_row(celex="32022R2554")]
    with pytest.raises(CellarParseError) as exc_info:
        parse_act_refs(rows)

    assert exc_info.value.details["parser"] == "parse_act_refs"
    assert exc_info.value.details["row_index"] == 0


def test_parse_case_law_items_maps_case_fields() -> None:
    rows = [
        sparql_row(
            other="https://publications.europa.eu/resource/cellar/case",
            celex="62019CJ0287",
            ecli="ECLI:EU:C:2020:897",
            courtFormation="Izba I",
        )
    ]
    items = parse_case_law_items(rows)
    assert len(items) == 1
    assert items[0].ecli == "ECLI:EU:C:2020:897"


def test_parse_bindings_reads_expected_structure() -> None:
    payload = sparql_payload([sparql_row(work="https://publications.europa.eu/resource/cellar/work")])
    bindings = parse_bindings(payload)
    assert len(bindings) == 1


def test_parse_act_detail_rejects_invalid_boolean() -> None:
    rows = [
        sparql_row(
            work="https://publications.europa.eu/resource/cellar/work",
            inForce="maybe",
        )
    ]
    with pytest.raises(CellarParseError, match="Invalid boolean") as exc_info:
        parse_act_detail(rows)

    assert exc_info.value.details["parser"] == "parse_act_detail"
    assert exc_info.value.details["field"] == "inForce"


def test_parse_act_detail_rejects_invalid_row_shape() -> None:
    with pytest.raises(CellarParseError, match="binding slot is not an object") as exc_info:
        parse_act_detail([{"work": "not-a-binding-slot"}])  # type: ignore[list-item]

    assert exc_info.value.details["parser"] == "parse_act_detail"
