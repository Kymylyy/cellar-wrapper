from __future__ import annotations

from typing import Any

import pytest

from cellar_wrapper.errors import CellarParseError
from cellar_wrapper.parser import (
    parse_act_detail,
    parse_act_refs,
    parse_article_annotation_items,
    parse_bindings,
    parse_case_law_items,
    parse_dossier_items,
    parse_nim_items,
    parse_relation_items,
)
from tests.helpers import sparql_payload, sparql_row


def test_parse_bindings_missing_results_raises() -> None:
    with pytest.raises(CellarParseError) as exc_info:
        parse_bindings({})

    assert exc_info.value.details["parser"] == "parse_bindings"
    assert exc_info.value.details["field"] == "results.bindings"


def test_parse_bindings_rejects_non_object_results() -> None:
    with pytest.raises(CellarParseError) as exc_info:
        parse_bindings({"results": None})

    assert exc_info.value.details["parser"] == "parse_bindings"
    assert exc_info.value.details["field"] == "results.bindings"


def test_parse_bindings_rejects_non_object_payload() -> None:
    with pytest.raises(CellarParseError) as exc_info:
        parse_bindings([])  # type: ignore[arg-type]

    assert exc_info.value.details["parser"] == "parse_bindings"
    assert exc_info.value.details["field"] == "payload"


def test_parse_act_refs_requires_uri_column() -> None:
    rows = [sparql_row(celex="32022R2554")]
    with pytest.raises(CellarParseError) as exc_info:
        parse_act_refs(rows)

    assert exc_info.value.details["parser"] == "parse_act_refs"
    assert exc_info.value.details["row_index"] == 0


def test_parse_act_refs_supports_explicit_uri_key() -> None:
    rows = [
        sparql_row(
            work="https://publications.europa.eu/resource/cellar/work",
            celex="32022R2554",
        )
    ]
    refs = parse_act_refs(rows, uri_key="work")

    assert len(refs) == 1
    assert refs[0].uri == "https://publications.europa.eu/resource/cellar/work"


def test_parse_case_law_items_maps_case_fields() -> None:
    rows = [
        sparql_row(
            uri="https://publications.europa.eu/resource/cellar/case",
            celex="62019CJ0287",
            ecli="ECLI:EU:C:2020:897",
            courtFormation="First Chamber",
            originCountry="http://publications.europa.eu/resource/authority/country/AUT",
        )
    ]
    items = parse_case_law_items(rows)
    assert len(items) == 1
    assert items[0].ecli == "ECLI:EU:C:2020:897"
    assert items[0].origin_country is not None


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


def test_parse_act_detail_collects_multi_value_fields() -> None:
    rows = [
        sparql_row(
            work="https://publications.europa.eu/resource/cellar/work",
            celex="32022R2554",
            inForce="1",
            eea="true",
            createdBy="http://publications.europa.eu/resource/authority/corporate-body/COM",
            responsibleAgent="http://publications.europa.eu/resource/authority/corporate-body/FISMA",
            addressesInstitution="http://publications.europa.eu/resource/authority/corporate-body/EUMS",
            signatoryName="M. Schulz",
        ),
        sparql_row(
            work="https://publications.europa.eu/resource/cellar/work",
            createdBy="http://publications.europa.eu/resource/authority/corporate-body/CONSIL",
            signatoryName="N. Schmit",
        ),
    ]
    detail = parse_act_detail(rows)
    assert detail is not None
    assert detail.in_force is True
    assert detail.eea_relevant is True
    assert len(detail.created_by_agents) == 2
    assert len(detail.signatory_names) == 2


def test_parse_act_detail_rejects_conflicting_scalar_values() -> None:
    rows = [
        sparql_row(
            work="https://publications.europa.eu/resource/cellar/work",
            celex="32022R2554",
            title="Title A",
        ),
        sparql_row(
            work="https://publications.europa.eu/resource/cellar/work",
            celex="32022R2554",
            title="Title B",
        ),
    ]
    with pytest.raises(CellarParseError, match="Conflicting scalar value") as exc_info:
        parse_act_detail(rows)

    assert exc_info.value.details["parser"] == "parse_act_detail"
    assert exc_info.value.details["field"] == "title"


def test_parse_act_detail_rejects_conflicting_work_uris() -> None:
    rows = [
        sparql_row(
            work="https://publications.europa.eu/resource/cellar/work-a",
            celex="32022R2554",
        ),
        sparql_row(
            work="https://publications.europa.eu/resource/cellar/work-b",
            celex="32022R2554",
        ),
    ]
    with pytest.raises(CellarParseError, match="Conflicting work URI") as exc_info:
        parse_act_detail(rows)

    assert exc_info.value.details["parser"] == "parse_act_detail"
    assert exc_info.value.details["field"] == "work"


def test_parse_dossier_items_maps_metadata_and_status_flags() -> None:
    rows = [
        sparql_row(
            uri="https://publications.europa.eu/resource/cellar/related",
            celex="52023PC0367",
            dossier="https://publications.europa.eu/resource/cellar/dossier",
            procedureCode="2023/0210/COD",
            procedureType="OLP",
            statusAdopted="0",
            statusPending="1",
            statusWithdrawn="false",
            producesAct="https://publications.europa.eu/resource/cellar/final-act",
            producesActCelex="32025R0001",
            relationType="dossier_contains_work",
            direction="incoming",
            predicate="cdm:dossier_contains_work",
        )
    ]
    items = parse_dossier_items(rows)
    assert len(items) == 1
    assert items[0].procedure_code == "2023/0210/COD"
    assert items[0].status_pending is True
    assert items[0].status_adopted is False
    assert items[0].status_withdrawn is False
    assert items[0].produces_act_celex == "32025R0001"


def test_parse_nim_items_maps_country() -> None:
    rows = [
        sparql_row(
            uri="https://publications.europa.eu/resource/cellar/nim",
            celex="72015L2366POL_258600",
            relationType="nims",
            direction="incoming",
            predicate="cdm:measure_national_implementing_implements_resource_legal",
            implementedByCountry="http://publications.europa.eu/resource/authority/country/POL",
        )
    ]
    items = parse_nim_items(rows)
    assert len(items) == 1
    assert items[0].implemented_by_country is not None


def test_parse_relation_items_ignores_annotation_columns() -> None:
    rows = [
        sparql_row(
            uri="https://publications.europa.eu/resource/cellar/related",
            celex="32024R0001",
            relationType="relation",
            direction="incoming",
            predicate="cdm:work_related_to_work",
            annotation="https://publications.europa.eu/resource/cellar/annotation",
        )
    ]
    items = parse_relation_items(rows)
    assert len(items) == 1
    assert not hasattr(items[0], "annotation_uri")


def test_parse_article_annotation_items_maps_qualifiers() -> None:
    rows = [
        sparql_row(
            uri="https://publications.europa.eu/resource/cellar/annotated",
            relationType="article_annotation",
            direction="incoming",
            predicate="cdm:resource_legal_amends_resource_legal",
            annotation="https://publications.europa.eu/resource/cellar/annotation",
            article="5",
            paragraph="1",
            subparagraph="a",
            point="i",
            commentOnLegalBasis="reference note",
        )
    ]
    items = parse_article_annotation_items(rows)
    assert len(items) == 1
    assert items[0].annotation_uri is not None
    assert items[0].annotation_article == "5"
    assert items[0].annotation_comment_on_legal_basis == "reference note"


def test_parse_article_annotation_items_handles_partial_qualifiers() -> None:
    rows = [
        sparql_row(
            uri="https://publications.europa.eu/resource/cellar/annotated",
            relationType="article_annotation",
            direction="incoming",
            predicate="cdm:resource_legal_amends_resource_legal",
            annotation="https://publications.europa.eu/resource/cellar/annotation",
        )
    ]
    items = parse_article_annotation_items(rows)
    assert len(items) == 1
    assert items[0].annotation_uri is not None
    assert items[0].annotation_article is None


def test_parse_act_detail_rejects_invalid_row_shape() -> None:
    bad_rows: list[Any] = [{"work": "not-a-binding-slot"}]
    with pytest.raises(CellarParseError, match="binding slot is not an object") as exc_info:
        parse_act_detail(bad_rows)

    assert exc_info.value.details["parser"] == "parse_act_detail"
