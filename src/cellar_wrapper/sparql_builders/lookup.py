"""SPARQL builders for lookup-oriented queries."""

from __future__ import annotations

from cellar_wrapper.constants import DEFAULT_LANGUAGE

from .common import language_uri, limit_offset, quote_literal, with_prefixes


def build_resolve_celex_query(celex: str, *, use_contains: bool) -> str:
    """Build CELEX-to-work URI resolution query."""
    celex_upper = celex.upper()
    if use_contains:
        token = celex_upper[1:] if len(celex_upper) > 1 else celex_upper
        filter_clause = f"FILTER(CONTAINS(UCASE(STR(?celex)), {quote_literal(token)}))"
    else:
        filter_clause = f"FILTER(UCASE(STR(?celex)) = {quote_literal(celex_upper)})"

    query = f"""
SELECT DISTINCT ?work ?celex WHERE {{
  ?work cdm:resource_legal_id_celex ?celex .
  {filter_clause}
}}
LIMIT 5
"""
    return with_prefixes(query)


def build_get_act_query(work_uri: str, *, lang: str = DEFAULT_LANGUAGE) -> str:
    """Build work metadata query."""
    lang_uri = language_uri(lang)
    query = f"""
SELECT DISTINCT ?work ?celex ?eli ?type ?inForce ?dateDocument ?dateEntryIntoForce ?dateEndOfValidity ?title WHERE {{
  BIND(<{work_uri}> AS ?work)
  OPTIONAL {{ ?work cdm:resource_legal_id_celex ?celex }}
  OPTIONAL {{ ?work cdm:resource_legal_eli ?eli }}
  OPTIONAL {{ ?work cdm:work_has_resource-type ?type }}
  OPTIONAL {{ ?work cdm:resource_legal_in-force ?inForce }}
  OPTIONAL {{ ?work cdm:work_date_document ?dateDocument }}
  OPTIONAL {{ ?work cdm:resource_legal_date_entry-into-force ?dateEntryIntoForce }}
  OPTIONAL {{ ?work cdm:resource_legal_date_end-of-validity ?dateEndOfValidity }}
  OPTIONAL {{
    ?expression cdm:expression_belongs_to_work ?work .
    ?expression cdm:expression_uses_language <{lang_uri}> .
    ?expression cdm:expression_title ?title .
  }}
}}
LIMIT 1
"""
    return with_prefixes(query)


def build_concept_query(work_uri: str, *, predicate: str) -> str:
    """Build concept lookup query (EuroVoc, subject-matter, directory code)."""
    query = f"""
SELECT DISTINCT ?concept ?label WHERE {{
  <{work_uri}> {predicate} ?concept .
  OPTIONAL {{
    ?concept skos:prefLabel ?label .
    FILTER(LANG(?label) = 'en' || LANG(?label) = '')
  }}
}}
ORDER BY ?concept
"""
    return with_prefixes(query)


def build_legal_basis_query(work_uri: str, *, limit: int, offset: int) -> str:
    """Build legal basis query."""
    query = f"""
SELECT DISTINCT ?other ?celex ?title ?date ?type ?relationType ?direction ?predicate WHERE {{
  {{
    ?other cdm:resource_legal_based_on_resource_legal <{work_uri}> .
    BIND('incoming' AS ?direction)
    BIND('based_on_resource_legal' AS ?relationType)
    BIND('cdm:resource_legal_based_on_resource_legal' AS ?predicate)
  }} UNION {{
    <{work_uri}> cdm:resource_legal_based_on_resource_legal ?other .
    BIND('outgoing' AS ?direction)
    BIND('based_on_resource_legal' AS ?relationType)
    BIND('cdm:resource_legal_based_on_resource_legal' AS ?predicate)
  }} UNION {{
    <{work_uri}> cdm:resource_legal_based_on_concept_treaty ?other .
    BIND('outgoing' AS ?direction)
    BIND('based_on_concept_treaty' AS ?relationType)
    BIND('cdm:resource_legal_based_on_concept_treaty' AS ?predicate)
  }}
  OPTIONAL {{ ?other cdm:resource_legal_id_celex ?celex }}
  OPTIONAL {{ ?other cdm:work_date_document ?date }}
  OPTIONAL {{ ?other cdm:work_has_resource-type ?type }}
  OPTIONAL {{
    ?expr cdm:expression_belongs_to_work ?other .
    ?expr cdm:expression_uses_language <{language_uri(DEFAULT_LANGUAGE)}> .
    ?expr cdm:expression_title ?title .
  }}
}}
ORDER BY DESC(?date)
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


def build_expressions_query(work_uri: str, *, limit: int, offset: int) -> str:
    """Build expressions query."""
    query = f"""
SELECT DISTINCT ?expression ?lang ?title WHERE {{
  ?expression cdm:expression_belongs_to_work <{work_uri}> .
  OPTIONAL {{ ?expression cdm:expression_uses_language ?lang }}
  OPTIONAL {{ ?expression cdm:expression_title ?title }}
}}
ORDER BY ?lang
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)
