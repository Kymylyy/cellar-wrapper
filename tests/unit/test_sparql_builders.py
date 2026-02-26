from __future__ import annotations

from cellar_wrapper.sparql import (
    PredicateSpec,
    build_relation_query,
    build_resolve_celex_query,
)


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
    assert "FILTER(STR(?date) > '2025-01-01')" in query
    assert ">=" not in query
    assert "resource-type/PROP_REG" in query
