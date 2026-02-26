from __future__ import annotations

import pytest

from cellar_wrapper.sparql import (
    PredicateSpec,
    build_article_annotations_query,
    build_concept_query,
    build_relation_query,
    build_resolve_celex_query,
    build_search_by_eurovoc_query,
)
from cellar_wrapper.sparql_builders.common import quote_literal


def test_build_resolve_celex_exact_uses_equals_filter() -> None:
    query = build_resolve_celex_query("32022R2554", use_contains=False)
    assert "FILTER(UCASE(STR(?celex)) = '32022R2554')" in query


def test_build_resolve_celex_contains_fallback() -> None:
    query = build_resolve_celex_query("32022R2554", use_contains=True)
    assert "CONTAINS(UCASE(STR(?celex)), '2022R2554')" in query


def test_relation_query_uses_since_greater_than() -> None:
    query = build_relation_query(
        "http://publications.europa.eu/resource/cellar/example",
        predicates=[PredicateSpec("cdm:work_cites_work", "cites")],
        direction="incoming",
        since="2025-01-01",
        resource_type="PROP_REG",
        limit=200,
        offset=0,
    )
    assert "FILTER(?date > '2025-01-01'^^xsd:date)" in query
    assert ">=" not in query
    assert "resource-type/PROP_REG" in query


def test_quote_literal_escapes_control_chars() -> None:
    literal = quote_literal("line1\nline2\r\t'quoted'\\path")
    assert literal == r"'line1\nline2\r\t\'quoted\'\\path'"


def test_build_concept_query_validates_predicate() -> None:
    with pytest.raises(ValueError, match="Unsupported concept predicate"):
        build_concept_query(
            "http://publications.europa.eu/resource/cellar/example",
            predicate="cdm:resource_legal_id_celex ?x ?y",
        )


def test_build_concept_query_has_limit_offset() -> None:
    query = build_concept_query(
        "http://publications.europa.eu/resource/cellar/example",
        predicate="cdm:work_is_about_concept_eurovoc",
        limit=7,
        offset=9,
    )
    assert "LIMIT 7" in query
    assert "OFFSET 9" in query


def test_search_by_eurovoc_query_matches_labels_only() -> None:
    query = build_search_by_eurovoc_query(
        ["payment"],
        resource_type=None,
        since=None,
        limit=50,
        offset=0,
    )
    assert "CONTAINS(LCASE(STR(?conceptLabel))" in query
    assert "CONTAINS(LCASE(STR(?concept))" not in query


def test_article_annotations_query_requests_article_level_qualifiers() -> None:
    query = build_article_annotations_query(
        "http://publications.europa.eu/resource/cellar/example",
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
            "http://publications.europa.eu/resource/cellar/example",
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
            "http://publications.europa.eu/resource/cellar/example",
            predicates=[PredicateSpec("cdm:work_cites_work", "cites")],
            direction="sideways",
            since=None,
            resource_type=None,
            limit=10,
            offset=0,
        )
