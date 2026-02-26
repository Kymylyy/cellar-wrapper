"""SPARQL builders for search and concept discovery."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime

from cellar_wrapper.constants import DEFAULT_LANGUAGE

from .common import (
    language_uri,
    limit_offset,
    quote_literal,
    resource_type_uri,
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
) -> str:
    """Build search by EuroVoc tags query."""
    tag_filters: list[str] = []
    for tag in tags:
        lit = quote_literal(tag)
        tag_filters.append(
            f"CONTAINS(LCASE(STR(?concept)), LCASE({lit})) || CONTAINS(LCASE(STR(?conceptLabel)), LCASE({lit}))"
        )
    filter_clause = " || ".join(tag_filters) if tag_filters else "true"

    type_clause = ""
    if resource_type is not None:
        type_clause = f"?work cdm:work_has_resource-type <{resource_type_uri(resource_type)}> ."

    query = f"""
SELECT DISTINCT ?work ?celex ?title ?date ?type WHERE {{
  ?work cdm:work_is_about_concept_eurovoc ?concept .
  OPTIONAL {{
    ?concept skos:prefLabel ?conceptLabel .
    FILTER(LANG(?conceptLabel) = 'en' || LANG(?conceptLabel) = '')
  }}
  FILTER({filter_clause})
  OPTIONAL {{ ?work cdm:resource_legal_id_celex ?celex }}
  OPTIONAL {{ ?work cdm:work_date_document ?date }}
  OPTIONAL {{ ?work cdm:work_has_resource-type ?type }}
  OPTIONAL {{
    ?expr cdm:expression_belongs_to_work ?work .
    ?expr cdm:expression_uses_language <{language_uri(lang)}> .
    ?expr cdm:expression_title ?title .
  }}
  {type_clause}
  {since_filter("date", since)}
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

    type_clause = ""
    if resource_type is not None:
        type_clause = f"?work cdm:work_has_resource-type <{resource_type_uri(resource_type)}> ."

    query = f"""
SELECT DISTINCT ?work ?celex ?title ?date ?type WHERE {{
  ?work cdm:resource_legal_is_about_subject-matter ?concept .
  OPTIONAL {{
    ?concept skos:prefLabel ?conceptLabel .
    FILTER(LANG(?conceptLabel) = 'en' || LANG(?conceptLabel) = '')
  }}
  FILTER({filter_clause})
  OPTIONAL {{ ?work cdm:resource_legal_id_celex ?celex }}
  OPTIONAL {{ ?work cdm:work_date_document ?date }}
  OPTIONAL {{ ?work cdm:work_has_resource-type ?type }}
  OPTIONAL {{
    ?expr cdm:expression_belongs_to_work ?work .
    ?expr cdm:expression_uses_language <{language_uri(lang)}> .
    ?expr cdm:expression_title ?title .
  }}
  {type_clause}
  {since_filter("date", since)}
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
    type_clause = ""
    if resource_type is not None:
        type_clause = f"?work cdm:work_has_resource-type <{resource_type_uri(resource_type)}> ."

    query = f"""
SELECT DISTINCT ?work ?celex ?title ?date ?type WHERE {{
  ?expr cdm:expression_belongs_to_work ?work .
  ?expr cdm:expression_uses_language <{language_uri(lang)}> .
  ?expr cdm:expression_title ?title .
  FILTER(CONTAINS(LCASE(STR(?title)), LCASE({quote_literal(keyword)})))
  OPTIONAL {{ ?work cdm:resource_legal_id_celex ?celex }}
  OPTIONAL {{ ?work cdm:work_date_document ?date }}
  OPTIONAL {{ ?work cdm:work_has_resource-type ?type }}
  {type_clause}
  {since_filter("date", since)}
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
    communic_uri = resource_type_uri("COMMUNIC")
    query = f"""
SELECT DISTINCT ?work ?celex ?title ?date ?type WHERE {{
  ?work cdm:work_has_resource-type <{communic_uri}> .
  OPTIONAL {{ ?work cdm:resource_legal_service_responsible ?service }}
  FILTER(CONTAINS(UCASE(STR(?service)), UCASE({quote_literal(dg)})))
  OPTIONAL {{ ?work cdm:resource_legal_id_celex ?celex }}
  OPTIONAL {{ ?work cdm:work_date_document ?date }}
  OPTIONAL {{ ?work cdm:work_has_resource-type ?type }}
  OPTIONAL {{
    ?expr cdm:expression_belongs_to_work ?work .
    ?expr cdm:expression_uses_language <{language_uri(lang)}> .
    ?expr cdm:expression_title ?title .
  }}
  {since_filter("date", since)}
}}
ORDER BY DESC(?date)
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


def build_find_eurovoc_concept_query(label: str, *, limit: int, offset: int) -> str:
    """Build EuroVoc concept lookup query."""
    query = f"""
SELECT DISTINCT ?concept ?label WHERE {{
  ?concept skos:prefLabel ?label .
  FILTER(LANG(?label) = 'en' || LANG(?label) = '')
  FILTER(CONTAINS(LCASE(STR(?label)), LCASE({quote_literal(label)})))
}}
ORDER BY ?label
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)
