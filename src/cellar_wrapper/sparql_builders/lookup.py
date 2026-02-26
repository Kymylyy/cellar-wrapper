"""SPARQL builders for lookup-oriented queries."""

from __future__ import annotations

from cellar_wrapper.constants import DEFAULT_LANGUAGE, DEFAULT_LIMIT, DEFAULT_OFFSET, PREDICATES

from .common import language_uri, limit_offset, quote_literal, safe_iri, with_prefixes

CONCEPT_PREDICATES = frozenset(
    {
        PREDICATES["work_is_about_concept_eurovoc"],
        PREDICATES["subject_matter"],
        PREDICATES["directory_code"],
    }
)


def build_resolve_celex_query(celex: str, *, use_contains: bool) -> str:
    """Build CELEX-to-work URI resolution query."""
    celex_upper = celex.upper()
    limit = 20 if use_contains else 5
    if use_contains:
        # CELLAR CELEX fallback: drop sector prefix (first char) and probe by token.
        token = celex_upper[1:] if len(celex_upper) > 1 else celex_upper
        filter_clause = f"FILTER(CONTAINS(UCASE(STR(?celex)), {quote_literal(token)}))"
    else:
        filter_clause = f"FILTER(UCASE(STR(?celex)) = {quote_literal(celex_upper)})"

    query = f"""
SELECT DISTINCT ?work ?celex WHERE {{
  ?work {PREDICATES["resource_legal_id_celex"]} ?celex .
  {filter_clause}
}}
LIMIT {limit}
"""
    return with_prefixes(query)


def build_get_act_query(work_uri: str, *, lang: str = DEFAULT_LANGUAGE) -> str:
    """Build work metadata query."""
    lang_uri = safe_iri(language_uri(lang), field="language_uri")
    work_iri = safe_iri(work_uri, field="work_uri")
    query = f"""
SELECT DISTINCT ?work ?celex ?eli ?type ?inForce ?dateDocument ?dateEntryIntoForce ?dateEndOfValidity ?title WHERE {{
  BIND(<{work_iri}> AS ?work)
  OPTIONAL {{ ?work {PREDICATES["resource_legal_id_celex"]} ?celex }}
  OPTIONAL {{ ?work {PREDICATES["resource_legal_eli"]} ?eli }}
  OPTIONAL {{ ?work {PREDICATES["work_has_resource_type"]} ?type }}
  OPTIONAL {{ ?work {PREDICATES["resource_legal_in_force"]} ?inForce }}
  OPTIONAL {{ ?work {PREDICATES["work_date_document"]} ?dateDocument }}
  OPTIONAL {{ ?work {PREDICATES["entry_into_force"]} ?dateEntryIntoForce }}
  OPTIONAL {{ ?work {PREDICATES["resource_legal_date_end_of_validity"]} ?dateEndOfValidity }}
  OPTIONAL {{
    ?expression {PREDICATES["expression_belongs_to_work"]} ?work .
    ?expression {PREDICATES["expression_uses_language"]} <{lang_uri}> .
    ?expression {PREDICATES["expression_title"]} ?title .
  }}
}}
LIMIT 1
"""
    return with_prefixes(query)


def build_concept_query(
    work_uri: str,
    *,
    predicate: str,
    limit: int = DEFAULT_LIMIT,
    offset: int = DEFAULT_OFFSET,
) -> str:
    """Build concept lookup query (EuroVoc, subject-matter, directory code)."""
    if predicate not in CONCEPT_PREDICATES:
        raise ValueError(f"Unsupported concept predicate: {predicate}")
    work_iri = safe_iri(work_uri, field="work_uri")

    query = f"""
SELECT DISTINCT ?concept ?label WHERE {{
  <{work_iri}> {predicate} ?concept .
  OPTIONAL {{
    ?concept skos:prefLabel ?label .
    FILTER(LANG(?label) = 'en' || LANG(?label) = '')
  }}
}}
ORDER BY ?concept
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


def build_legal_basis_query(work_uri: str, *, limit: int, offset: int) -> str:
    """Build legal basis query."""
    work_iri = safe_iri(work_uri, field="work_uri")
    default_lang_iri = safe_iri(language_uri(DEFAULT_LANGUAGE), field="language_uri")
    query = f"""
SELECT DISTINCT ?other ?celex ?title ?date ?type ?relationType ?direction ?predicate WHERE {{
  {{
    ?other {PREDICATES["based_on"]} <{work_iri}> .
    BIND({quote_literal("incoming")} AS ?direction)
    BIND({quote_literal("based_on_resource_legal")} AS ?relationType)
    BIND({quote_literal(PREDICATES["based_on"])} AS ?predicate)
  }} UNION {{
    <{work_iri}> {PREDICATES["based_on"]} ?other .
    BIND({quote_literal("outgoing")} AS ?direction)
    BIND({quote_literal("based_on_resource_legal")} AS ?relationType)
    BIND({quote_literal(PREDICATES["based_on"])} AS ?predicate)
  }} UNION {{
    <{work_iri}> {PREDICATES["based_on_concept_treaty"]} ?other .
    BIND({quote_literal("outgoing")} AS ?direction)
    BIND({quote_literal("based_on_concept_treaty")} AS ?relationType)
    BIND({quote_literal(PREDICATES["based_on_concept_treaty"])} AS ?predicate)
  }}
  OPTIONAL {{ ?other {PREDICATES["resource_legal_id_celex"]} ?celex }}
  OPTIONAL {{ ?other {PREDICATES["work_date_document"]} ?date }}
  OPTIONAL {{ ?other {PREDICATES["work_has_resource_type"]} ?type }}
  OPTIONAL {{
    ?expr {PREDICATES["expression_belongs_to_work"]} ?other .
    ?expr {PREDICATES["expression_uses_language"]} <{default_lang_iri}> .
    ?expr {PREDICATES["expression_title"]} ?title .
  }}
}}
ORDER BY DESC(?date)
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


def build_expressions_query(work_uri: str, *, limit: int, offset: int) -> str:
    """Build expressions query."""
    work_iri = safe_iri(work_uri, field="work_uri")
    query = f"""
SELECT DISTINCT ?expression ?lang ?title WHERE {{
  ?expression {PREDICATES["expression_belongs_to_work"]} <{work_iri}> .
  OPTIONAL {{ ?expression {PREDICATES["expression_uses_language"]} ?lang }}
  OPTIONAL {{ ?expression {PREDICATES["expression_title"]} ?title }}
}}
ORDER BY ?lang
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)
