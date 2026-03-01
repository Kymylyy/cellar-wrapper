from __future__ import annotations

import re

import pytest

from cellar_wrapper.constants import PREDICATES
from cellar_wrapper.sparql import (
    PredicateSpec,
    build_article_annotations_query,
    build_concept_query,
    build_dossier_query,
    build_find_eurovoc_concept_query,
    build_get_act_query,
    build_national_decisions_query,
    build_relation_query,
    build_resolve_celex_query,
    build_search_by_eurovoc_query,
    build_search_by_subject_matter_query,
    build_search_communications_query,
)
from cellar_wrapper.sparql_builders.common import quote_literal, safe_iri, since_filter


def test_build_resolve_celex_exact_uses_equals_filter() -> None:
    query = build_resolve_celex_query("32022R2554", use_contains=False)
    assert "FILTER(UCASE(STR(?celex)) = '32022R2554')" in query


def test_build_resolve_celex_contains_fallback() -> None:
    query = build_resolve_celex_query("32022R2554", use_contains=True)
    assert "CONTAINS(UCASE(STR(?celex)), '2022R2554')" in query
    assert "LIMIT 20" in query


def test_build_resolve_celex_exact_uses_smaller_limit() -> None:
    query = build_resolve_celex_query("32022R2554", use_contains=False)
    assert "LIMIT 5" in query


def test_relation_query_uses_since_date_time_filter() -> None:
    query = build_relation_query(
        "https://publications.europa.eu/resource/cellar/example",
        predicates=[PredicateSpec("cdm:work_cites_work", "cites")],
        direction="incoming",
        since="2025-01-01",
        resource_type="PROP_REG",
        limit=200,
        offset=0,
    )
    assert "FILTER(!BOUND(?date) || ?date > '2025-01-01T00:00:00Z'^^xsd:dateTime)" in query
    assert "resource-type/PROP_REG" in query


def test_relation_query_monitoring_filter_is_strict() -> None:
    query = build_relation_query(
        "https://publications.europa.eu/resource/cellar/example",
        predicates=[PredicateSpec("cdm:work_cites_work", "cites")],
        direction="incoming",
        since="2025-01-01",
        resource_type=None,
        limit=10,
        offset=0,
        include_undated=False,
    )
    assert "FILTER(BOUND(?date) && ?date > '2025-01-01T00:00:00Z'^^xsd:dateTime)" in query


def test_quote_literal_escapes_control_chars() -> None:
    literal = quote_literal("line1\nline2\r\t'quoted'\\path")
    assert literal == r"'line1\nline2\r\t\'quoted\'\\path'"


def test_build_concept_query_validates_predicate() -> None:
    with pytest.raises(ValueError, match="Unsupported concept predicate"):
        build_concept_query(
            "https://publications.europa.eu/resource/cellar/example",
            predicate="cdm:resource_legal_id_celex ?x ?y",
        )


def test_build_concept_query_has_limit_offset() -> None:
    query = build_concept_query(
        "https://publications.europa.eu/resource/cellar/example",
        predicate="cdm:work_is_about_concept_eurovoc",
        limit=7,
        offset=9,
    )
    assert "LIMIT 7" in query
    assert "OFFSET 9" in query


def test_search_by_eurovoc_query_filters_by_concept_values() -> None:
    query = build_search_by_eurovoc_query(
        ["http://eurovoc.europa.eu/2220"],
        resource_type=None,
        since=None,
        limit=50,
        offset=0,
    )
    assert "VALUES ?concept { <http://eurovoc.europa.eu/2220> }" in query
    assert "CONTAINS(LCASE(STR(?conceptLabel))" not in query
    assert "?concept skos:prefLabel ?conceptLabel ." not in query


def test_search_by_subject_matter_query_filters_by_concept_values() -> None:
    query = build_search_by_subject_matter_query(
        ["http://publications.europa.eu/resource/authority/subject-matter/PDON"],
        resource_type=None,
        since=None,
        limit=50,
        offset=0,
    )
    assert (
        "VALUES ?concept { <http://publications.europa.eu/resource/authority/subject-matter/PDON> }"
        in query
    )
    assert "CONTAINS(LCASE(STR(?conceptLabel))" not in query
    assert "?concept skos:prefLabel ?conceptLabel ." not in query


def test_search_by_subject_matter_query_rejects_empty_concept_uris() -> None:
    with pytest.raises(ValueError, match="concept_uris cannot be empty"):
        build_search_by_subject_matter_query(
            [],
            resource_type=None,
            since=None,
            limit=50,
            offset=0,
        )


def test_article_annotations_query_requests_article_level_qualifiers() -> None:
    query = build_article_annotations_query(
        "https://publications.europa.eu/resource/cellar/example",
        limit=20,
        offset=0,
    )
    assert "?article" in query
    assert "?paragraph" in query
    assert "?subparagraph" in query
    assert "?commentOnLegalBasis" in query


def test_relation_query_rejects_empty_predicates() -> None:
    with pytest.raises(ValueError, match="predicates cannot be empty"):
        build_relation_query(
            "https://publications.europa.eu/resource/cellar/example",
            predicates=[],
            direction="incoming",
            since=None,
            resource_type=None,
            limit=10,
            offset=0,
        )


def test_relation_query_rejects_bad_direction() -> None:
    with pytest.raises(ValueError, match="Unsupported direction"):
        build_relation_query(
            "https://publications.europa.eu/resource/cellar/example",
            predicates=[PredicateSpec("cdm:work_cites_work", "cites")],
            direction="sideways",
            since=None,
            resource_type=None,
            limit=10,
            offset=0,
        )


def test_relation_query_escapes_bind_relation_type_literal() -> None:
    query = build_relation_query(
        "https://publications.europa.eu/resource/cellar/example",
        predicates=[PredicateSpec("cdm:work_cites_work", "rel'ation")],
        direction="incoming",
        since=None,
        resource_type=None,
        limit=10,
        offset=0,
    )
    assert r"BIND('rel\'ation' AS ?relationType)" in query


def test_safe_iri_accepts_valid_http_iri() -> None:
    assert (
        safe_iri("https://publications.europa.eu/resource/cellar/example", field="work_uri")
        == "https://publications.europa.eu/resource/cellar/example"
    )


@pytest.mark.parametrize(
    ("candidate", "match"),
    [
        ("", "cannot be empty"),
        ("http://example.com/<bad>", "Invalid IRI"),
        ("javascript:alert(1)", "Invalid IRI"),
        ("https://example.com/o'hara", "Invalid IRI"),
        ("https://example.com/white space", "contains whitespace"),
    ],
)
def test_safe_iri_rejects_invalid_values(candidate: str, match: str) -> None:
    with pytest.raises(ValueError, match=match):
        safe_iri(candidate, field="test")


def test_since_filter_include_undated() -> None:
    clause = since_filter("date", "2025-01-01", include_undated=True)
    assert clause == "FILTER(!BOUND(?date) || ?date > '2025-01-01T00:00:00Z'^^xsd:dateTime)"


def test_since_filter_strict_monitoring() -> None:
    clause = since_filter("date", "2025-01-01T10:11:12Z", include_undated=False)
    assert clause == "FILTER(BOUND(?date) && ?date > '2025-01-01T10:11:12Z'^^xsd:dateTime)"


def test_build_dossier_query_excludes_self_reference() -> None:
    query = build_dossier_query(
        "https://publications.europa.eu/resource/cellar/example",
        limit=10,
        offset=0,
    )
    assert "FILTER(?other != <https://publications.europa.eu/resource/cellar/example>)" in query


def test_build_get_act_query_includes_enriched_metadata_predicates() -> None:
    query = build_get_act_query("https://publications.europa.eu/resource/cellar/example")
    assert "cdm:work_created_by_agent" in query
    assert "cdm:resource_legal_responsibility_of_agent" in query
    assert "cdm:resource_legal_eea" in query
    assert "cdm:resource_legal_addresses_institution" in query
    assert "cdm:resource_legal_signatory_name2" in query


def test_build_dossier_query_includes_procedure_metadata() -> None:
    query = build_dossier_query(
        "https://publications.europa.eu/resource/cellar/example",
        limit=10,
        offset=0,
    )
    assert "cdm:procedure_code_interinstitutional_reference_procedure" in query
    assert "cdm:procedure_code_interinstitutional_has_type" in query
    assert "cdm:dossier_produces_resource_legal" in query
    assert "?statusAdopted" in query
    assert "?statusPending" in query
    assert "?statusWithdrawn" in query


def test_build_dossier_query_windows_items_in_subquery() -> None:
    query = build_dossier_query(
        "https://publications.europa.eu/resource/cellar/example",
        limit=7,
        offset=3,
    )
    subquery = re.search(
        r"SELECT DISTINCT\s+\?dossier\s+\?other\s+\?date\s+WHERE\s*\{.*?\}\s*"
        r"ORDER BY\s+\?date\s+\?other(?:\s+\?[A-Za-z_][A-Za-z0-9_]*)*\s+LIMIT\s+7\s+OFFSET\s+3",
        query,
        re.DOTALL,
    )
    assert subquery is not None


def test_build_dossier_query_keeps_outer_projection_for_parser() -> None:
    query = build_dossier_query(
        "https://publications.europa.eu/resource/cellar/example",
        limit=10,
        offset=0,
    )
    select_match = re.search(
        r"SELECT DISTINCT\s+(?P<select_clause>.*?)\s+WHERE\s*\{",
        query,
        re.DOTALL,
    )
    assert select_match is not None
    select_clause = select_match.group("select_clause")
    expected_vars = (
        "?dossier",
        "?procedureCode",
        "?procedureType",
        "?statusAdopted",
        "?statusPending",
        "?statusWithdrawn",
        "?producesAct",
        "?producesActCelex",
        "?other",
        "?celex",
        "?title",
        "?date",
        "?type",
        "?relationType",
        "?direction",
        "?predicate",
    )
    for var in expected_vars:
        assert var in select_clause


def test_build_dossier_query_orders_inner_and_outer_by_date_other() -> None:
    query = build_dossier_query(
        "https://publications.europa.eu/resource/cellar/example",
        limit=11,
        offset=4,
    )
    order_by_matches = list(re.finditer(r"ORDER BY\s+\?date\s+\?other", query))
    assert len(order_by_matches) == 2
    tail_after_outer_order = query[order_by_matches[-1].end() :]
    assert "LIMIT 11" not in tail_after_outer_order
    assert "OFFSET 4" not in tail_after_outer_order


def test_build_dossier_query_nests_produces_act_celex_under_produces_act_optional() -> None:
    query = build_dossier_query(
        "https://publications.europa.eu/resource/cellar/example",
        limit=10,
        offset=0,
    )
    nested_optional = re.search(
        rf"OPTIONAL\s*\{{\s*\?dossier\s+{re.escape(PREDICATES['dossier_produces_resource_legal'])}"
        r"\s+\?producesAct\s*\.\s*OPTIONAL\s*\{\s*\?producesAct\s+"
        rf"{re.escape(PREDICATES['resource_legal_id_celex'])}\s+\?producesActCelex\s*\}}\s*\}}",
        query,
        re.DOTALL,
    )
    assert nested_optional is not None


def test_build_national_decisions_query_can_filter_by_country() -> None:
    query = build_national_decisions_query(
        "32022R2554",
        since="2025-01-01",
        country="DEU",
        limit=10,
        offset=0,
    )
    assert "cdm:case-law_originates_in_country" in query
    assert "CONTAINS(UCASE(STR(?originCountry)), 'DEU')" in query


def test_search_communications_requires_service_binding() -> None:
    query = build_search_communications_query("FISMA", since=None, limit=10, offset=0)
    assert "?work cdm:resource_legal_service_responsible ?service ." in query
    assert "OPTIONAL { ?work cdm:resource_legal_service_responsible ?service }" not in query


def test_find_eurovoc_concept_filters_to_eurovoc_namespace() -> None:
    query = build_find_eurovoc_concept_query("payment", limit=10, offset=0)
    assert "STRSTARTS(STR(?concept), 'http://eurovoc.europa.eu/')" in query


def test_directory_code_predicate_targets_concept_relation() -> None:
    assert PREDICATES["directory_code"] == "cdm:resource_legal_is_about_concept_directory-code"
