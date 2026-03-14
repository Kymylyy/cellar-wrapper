"""SPARQL builders for search and concept discovery."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime

from cellar_wrapper.constants import DEFAULT_LANGUAGE, PREDICATES

from .common import (
    date_bounds_filter,
    language_uri,
    limit_offset,
    quote_literal,
    resource_type_clause,
    resource_type_uri,
    safe_iri,
    with_prefixes,
)


def build_search_by_eurovoc_query(
    tags: Sequence[str],
    *,
    resource_types: Sequence[str] | None,
    since: date | datetime | str | None,
    limit: int,
    offset: int,
    to: date | datetime | str | None = None,
    lang: str = DEFAULT_LANGUAGE,
    include_undated: bool = True,
) -> str:
    """Build search by EuroVoc concept URI query."""
    concept_values: list[str] = []
    for concept_uri in tags:
        concept_values.append(f"<{safe_iri(concept_uri, field='eurovoc_concept_uri')}>")
    if not concept_values:
        raise ValueError("concept_uris cannot be empty")
    values_clause = " ".join(concept_values)
    lang_iri = language_uri(lang)
    type_clause = (
        f'OPTIONAL {{ ?work {PREDICATES["work_has_resource_type"]} ?type }}'
        if resource_types is None
        else resource_type_clause("work", resource_types)
    )

    query = f"""
SELECT DISTINCT ?work ?celex ?title ?date ?type WHERE {{
  ?work {PREDICATES["work_is_about_concept_eurovoc"]} ?concept .
  VALUES ?concept {{ {values_clause} }}
  OPTIONAL {{ ?work {PREDICATES["resource_legal_id_celex"]} ?celex }}
  OPTIONAL {{ ?work {PREDICATES["work_date_document"]} ?date }}
  {type_clause}
  OPTIONAL {{
    ?expr {PREDICATES["expression_belongs_to_work"]} ?work .
    ?expr {PREDICATES["expression_uses_language"]} <{lang_iri}> .
    ?expr {PREDICATES["expression_title"]} ?title .
  }}
  {date_bounds_filter("date", since=since, to=to, include_undated=include_undated)}
}}
ORDER BY DESC(?date)
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


def build_search_by_subject_matter_query(
    concept_uris: Sequence[str],
    *,
    resource_types: Sequence[str] | None,
    since: date | datetime | str | None,
    limit: int,
    offset: int,
    to: date | datetime | str | None = None,
    lang: str = DEFAULT_LANGUAGE,
) -> str:
    """Build search by subject-matter concept URI query."""
    concept_values: list[str] = []
    for concept_uri in concept_uris:
        concept_values.append(f"<{safe_iri(concept_uri, field='subject_matter_concept_uri')}>")
    if not concept_values:
        raise ValueError("concept_uris cannot be empty")
    values_clause = " ".join(concept_values)
    lang_iri = language_uri(lang)
    type_clause = (
        f'OPTIONAL {{ ?work {PREDICATES["work_has_resource_type"]} ?type }}'
        if resource_types is None
        else resource_type_clause("work", resource_types)
    )

    query = f"""
SELECT DISTINCT ?work ?celex ?title ?date ?type WHERE {{
  ?work {PREDICATES["subject_matter"]} ?concept .
  VALUES ?concept {{ {values_clause} }}
  OPTIONAL {{ ?work {PREDICATES["resource_legal_id_celex"]} ?celex }}
  OPTIONAL {{ ?work {PREDICATES["work_date_document"]} ?date }}
  {type_clause}
  OPTIONAL {{
    ?expr {PREDICATES["expression_belongs_to_work"]} ?work .
    ?expr {PREDICATES["expression_uses_language"]} <{lang_iri}> .
    ?expr {PREDICATES["expression_title"]} ?title .
  }}
  {date_bounds_filter("date", since=since, to=to, include_undated=True)}
}}
ORDER BY DESC(?date)
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


def build_search_by_title_query(
    keyword: str,
    *,
    resource_types: Sequence[str] | None,
    since: date | datetime | str | None,
    limit: int,
    offset: int,
    to: date | datetime | str | None = None,
    lang: str = DEFAULT_LANGUAGE,
) -> str:
    """Build search by title keyword query."""
    lang_iri = language_uri(lang)
    type_clause = (
        f'OPTIONAL {{ ?work {PREDICATES["work_has_resource_type"]} ?type }}'
        if resource_types is None
        else resource_type_clause("work", resource_types)
    )

    query = f"""
SELECT DISTINCT ?work ?celex ?title ?date ?type WHERE {{
  ?expr {PREDICATES["expression_belongs_to_work"]} ?work .
  ?expr {PREDICATES["expression_uses_language"]} <{lang_iri}> .
  ?expr {PREDICATES["expression_title"]} ?title .
  FILTER(CONTAINS(LCASE(STR(?title)), LCASE({quote_literal(keyword)})))
  OPTIONAL {{ ?work {PREDICATES["resource_legal_id_celex"]} ?celex }}
  OPTIONAL {{ ?work {PREDICATES["work_date_document"]} ?date }}
  {type_clause}
  {date_bounds_filter("date", since=since, to=to, include_undated=True)}
}}
ORDER BY DESC(?date)
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


def build_search_communications_query(
    dg: str,
    *,
    since: date | datetime | str | None,
    limit: int,
    offset: int,
    to: date | datetime | str | None = None,
    lang: str = DEFAULT_LANGUAGE,
) -> str:
    """Build search query for Commission communications by responsible service."""
    communic_uri = resource_type_uri("COMMUNIC")
    lang_iri = language_uri(lang)
    query = f"""
SELECT DISTINCT ?work ?celex ?title ?date ?type WHERE {{
  ?work {PREDICATES["work_has_resource_type"]} <{communic_uri}> .
  ?work {PREDICATES["resource_legal_service_responsible"]} ?service .
  FILTER(CONTAINS(UCASE(STR(?service)), UCASE({quote_literal(dg)})))
  OPTIONAL {{ ?work {PREDICATES["resource_legal_id_celex"]} ?celex }}
  OPTIONAL {{ ?work {PREDICATES["work_date_document"]} ?date }}
  OPTIONAL {{ ?work {PREDICATES["work_has_resource_type"]} ?type }}
  OPTIONAL {{
    ?expr {PREDICATES["expression_belongs_to_work"]} ?work .
    ?expr {PREDICATES["expression_uses_language"]} <{lang_iri}> .
    ?expr {PREDICATES["expression_title"]} ?title .
  }}
  {date_bounds_filter("date", since=since, to=to, include_undated=True)}
}}
ORDER BY DESC(?date)
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


def build_find_eurovoc_concept_query(label: str, *, limit: int, offset: int) -> str:
    """Build EuroVoc concept lookup query."""
    eurovoc_prefix = safe_iri("http://eurovoc.europa.eu/", field="eurovoc_concept_prefix")
    query = f"""
SELECT DISTINCT ?concept ?label WHERE {{
  ?concept skos:prefLabel ?label .
  FILTER(LANG(?label) = 'en' || LANG(?label) = '')
  FILTER(STRSTARTS(STR(?concept), {quote_literal(eurovoc_prefix)}))
  FILTER(CONTAINS(LCASE(STR(?label)), LCASE({quote_literal(label)})))
}}
ORDER BY ?label
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)
