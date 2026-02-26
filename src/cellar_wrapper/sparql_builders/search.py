"""SPARQL builders for search and concept discovery."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime

from cellar_wrapper.constants import DEFAULT_LANGUAGE, PREDICATES

from .common import (
    language_uri,
    limit_offset,
    quote_literal,
    resource_type_uri,
    safe_iri,
    since_filter,
    with_prefixes,
)


def build_search_by_eurovoc_query(
    tags: Sequence[str],
    *,
    resource_type: str | None,
    since: date | datetime | str | None,
    limit: int,
    offset: int,
    lang: str = DEFAULT_LANGUAGE,
    include_undated: bool = True,
) -> str:
    """Build search by EuroVoc tags query."""
    tag_filters: list[str] = []
    for tag in tags:
        lit = quote_literal(tag)
        tag_filters.append(f"CONTAINS(LCASE(STR(?conceptLabel)), LCASE({lit}))")
    filter_clause = " || ".join(tag_filters) if tag_filters else "true"
    lang_iri = safe_iri(language_uri(lang), field="language_uri")

    type_clause = ""
    if resource_type is not None:
        type_iri = safe_iri(resource_type_uri(resource_type), field="resource_type_uri")
        type_clause = f"?work {PREDICATES['work_has_resource_type']} <{type_iri}> ."

    query = f"""
SELECT DISTINCT ?work ?celex ?title ?date ?type WHERE {{
  ?work {PREDICATES["work_is_about_concept_eurovoc"]} ?concept .
  OPTIONAL {{
    ?concept skos:prefLabel ?conceptLabel .
    FILTER(LANG(?conceptLabel) = 'en' || LANG(?conceptLabel) = '')
  }}
  FILTER({filter_clause})
  OPTIONAL {{ ?work {PREDICATES["resource_legal_id_celex"]} ?celex }}
  OPTIONAL {{ ?work {PREDICATES["work_date_document"]} ?date }}
  OPTIONAL {{ ?work {PREDICATES["work_has_resource_type"]} ?type }}
  OPTIONAL {{
    ?expr {PREDICATES["expression_belongs_to_work"]} ?work .
    ?expr {PREDICATES["expression_uses_language"]} <{lang_iri}> .
    ?expr {PREDICATES["expression_title"]} ?title .
  }}
  {type_clause}
  {since_filter("date", since, include_undated=include_undated)}
}}
ORDER BY DESC(?date)
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


def build_search_by_subject_matter_query(
    codes: Sequence[str],
    *,
    resource_type: str | None,
    since: date | datetime | str | None,
    limit: int,
    offset: int,
    lang: str = DEFAULT_LANGUAGE,
) -> str:
    """Build search by subject-matter code query."""
    code_filters: list[str] = []
    for code in codes:
        lit = quote_literal(code)
        code_filters.append(
            f"CONTAINS(LCASE(STR(?concept)), LCASE({lit})) || CONTAINS(LCASE(STR(?conceptLabel)), LCASE({lit}))"
        )
    filter_clause = " || ".join(code_filters) if code_filters else "true"
    lang_iri = safe_iri(language_uri(lang), field="language_uri")

    type_clause = ""
    if resource_type is not None:
        type_iri = safe_iri(resource_type_uri(resource_type), field="resource_type_uri")
        type_clause = f"?work {PREDICATES['work_has_resource_type']} <{type_iri}> ."

    query = f"""
SELECT DISTINCT ?work ?celex ?title ?date ?type WHERE {{
  ?work {PREDICATES["subject_matter"]} ?concept .
  OPTIONAL {{
    ?concept skos:prefLabel ?conceptLabel .
    FILTER(LANG(?conceptLabel) = 'en' || LANG(?conceptLabel) = '')
  }}
  FILTER({filter_clause})
  OPTIONAL {{ ?work {PREDICATES["resource_legal_id_celex"]} ?celex }}
  OPTIONAL {{ ?work {PREDICATES["work_date_document"]} ?date }}
  OPTIONAL {{ ?work {PREDICATES["work_has_resource_type"]} ?type }}
  OPTIONAL {{
    ?expr {PREDICATES["expression_belongs_to_work"]} ?work .
    ?expr {PREDICATES["expression_uses_language"]} <{lang_iri}> .
    ?expr {PREDICATES["expression_title"]} ?title .
  }}
  {type_clause}
  {since_filter("date", since, include_undated=True)}
}}
ORDER BY DESC(?date)
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


def build_search_by_title_query(
    keyword: str,
    *,
    resource_type: str | None,
    since: date | datetime | str | None,
    limit: int,
    offset: int,
    lang: str = DEFAULT_LANGUAGE,
) -> str:
    """Build search by title keyword query."""
    lang_iri = safe_iri(language_uri(lang), field="language_uri")
    type_clause = ""
    if resource_type is not None:
        type_iri = safe_iri(resource_type_uri(resource_type), field="resource_type_uri")
        type_clause = f"?work {PREDICATES['work_has_resource_type']} <{type_iri}> ."

    query = f"""
SELECT DISTINCT ?work ?celex ?title ?date ?type WHERE {{
  ?expr {PREDICATES["expression_belongs_to_work"]} ?work .
  ?expr {PREDICATES["expression_uses_language"]} <{lang_iri}> .
  ?expr {PREDICATES["expression_title"]} ?title .
  FILTER(CONTAINS(LCASE(STR(?title)), LCASE({quote_literal(keyword)})))
  OPTIONAL {{ ?work {PREDICATES["resource_legal_id_celex"]} ?celex }}
  OPTIONAL {{ ?work {PREDICATES["work_date_document"]} ?date }}
  OPTIONAL {{ ?work {PREDICATES["work_has_resource_type"]} ?type }}
  {type_clause}
  {since_filter("date", since, include_undated=True)}
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
    lang: str = DEFAULT_LANGUAGE,
) -> str:
    """Build search query for Commission communications by responsible service."""
    communic_uri = safe_iri(resource_type_uri("COMMUNIC"), field="resource_type_uri")
    lang_iri = safe_iri(language_uri(lang), field="language_uri")
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
  {since_filter("date", since, include_undated=True)}
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
