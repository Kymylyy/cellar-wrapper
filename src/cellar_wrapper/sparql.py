"""SPARQL query builders for CELLAR wrapper."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime

from cellar_wrapper.constants import (
    DEFAULT_LANGUAGE,
    DEFAULT_LIMIT,
    DEFAULT_OFFSET,
    LANGUAGE_URI_TEMPLATE,
    RESOURCE_TYPE_URI_TEMPLATE,
    SPARQL_PREFIXES,
)


@dataclass(frozen=True)
class PredicateSpec:
    """Predicate with human relation label."""

    iri: str
    relation_type: str


def _quote_literal(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def _date_literal(value: date | datetime | str) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value


def _language_uri(lang: str) -> str:
    return LANGUAGE_URI_TEMPLATE.format(lang=lang.upper())


def _resource_type_uri(resource_type: str) -> str:
    return RESOURCE_TYPE_URI_TEMPLATE.format(resource_type=resource_type)


def _with_prefixes(body: str) -> str:
    return f"{SPARQL_PREFIXES}\n\n{body.strip()}"


def _limit_offset(limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET) -> str:
    return f"LIMIT {limit}\nOFFSET {offset}"


def _since_filter(var_name: str, since: date | datetime | str | None) -> str:
    if since is None:
        return ""
    literal = _quote_literal(_date_literal(since))
    return f"FILTER(STR(?{var_name}) > {literal})"


def _resource_type_clause(resource_type: str | None) -> str:
    if resource_type is None:
        return ""
    return f"?other cdm:work_has_resource-type <{_resource_type_uri(resource_type)}> ."


def build_resolve_celex_query(celex: str, *, use_contains: bool) -> str:
    """Build CELEX-to-work URI resolution query."""
    celex_upper = celex.upper()
    if use_contains:
        # Fallback token intentionally drops first char due to documented CELEX matching quirks.
        token = celex_upper[1:] if len(celex_upper) > 1 else celex_upper
        filter_clause = f"FILTER(CONTAINS(UCASE(STR(?celex)), {_quote_literal(token)}))"
    else:
        filter_clause = f"FILTER(UCASE(STR(?celex)) = {_quote_literal(celex_upper)})"

    query = f"""
SELECT DISTINCT ?work ?celex WHERE {{
  ?work cdm:resource_legal_id_celex ?celex .
  {filter_clause}
}}
LIMIT 5
"""
    return _with_prefixes(query)


def build_get_act_query(work_uri: str, *, lang: str = DEFAULT_LANGUAGE) -> str:
    """Build work metadata query."""
    lang_uri = _language_uri(lang)
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
    return _with_prefixes(query)


def build_concept_query(work_uri: str, *, predicate: str) -> str:
    """Build concept lookup query (EuroVoc or subject-matter)."""
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
    return _with_prefixes(query)


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
    ?expr cdm:expression_uses_language <{_language_uri(DEFAULT_LANGUAGE)}> .
    ?expr cdm:expression_title ?title .
  }}
}}
ORDER BY DESC(?date)
{_limit_offset(limit, offset)}
"""
    return _with_prefixes(query)


def build_expressions_query(work_uri: str, *, limit: int, offset: int) -> str:
    """Build expressions query."""
    query = f"""
SELECT DISTINCT ?expression ?lang ?title WHERE {{
  ?expression cdm:expression_belongs_to_work <{work_uri}> .
  OPTIONAL {{ ?expression cdm:expression_uses_language ?lang }}
  OPTIONAL {{ ?expression cdm:expression_title ?title }}
}}
ORDER BY ?lang
{_limit_offset(limit, offset)}
"""
    return _with_prefixes(query)


def build_relation_query(
    work_uri: str,
    *,
    predicates: Sequence[PredicateSpec],
    direction: str,
    since: date | datetime | str | None,
    resource_type: str | None,
    limit: int,
    offset: int,
    lang: str = DEFAULT_LANGUAGE,
) -> str:
    """Build generic relation query over one or more predicates."""
    unions: list[str] = []
    for spec in predicates:
        if direction in {"incoming", "both"}:
            unions.append(
                f"""
  {{
    ?other {spec.iri} <{work_uri}> .
    BIND('incoming' AS ?direction)
    BIND('{spec.relation_type}' AS ?relationType)
    BIND('{spec.iri}' AS ?predicate)
  }}
""".strip()
            )
        if direction in {"outgoing", "both"}:
            unions.append(
                f"""
  {{
    <{work_uri}> {spec.iri} ?other .
    BIND('outgoing' AS ?direction)
    BIND('{spec.relation_type}' AS ?relationType)
    BIND('{spec.iri}' AS ?predicate)
  }}
""".strip()
            )

    union_block = " UNION\n".join(unions)
    since_clause = _since_filter("date", since)
    type_clause = _resource_type_clause(resource_type)

    query = f"""
SELECT DISTINCT ?other ?celex ?title ?date ?type ?direction ?relationType ?predicate ?ecli ?courtFormation ?advocateGeneral WHERE {{
{union_block}
  OPTIONAL {{ ?other cdm:resource_legal_id_celex ?celex }}
  OPTIONAL {{ ?other cdm:work_date_document ?date }}
  OPTIONAL {{ ?other cdm:work_has_resource-type ?type }}
  OPTIONAL {{ ?other cdm:case-law_ecli ?ecli }}
  OPTIONAL {{ ?other cdm:case-law_delivered_by_court-formation ?courtFormation }}
  OPTIONAL {{ ?other cdm:case-law_delivered_by_advocate-general ?advocateGeneral }}
  OPTIONAL {{
    ?expr cdm:expression_belongs_to_work ?other .
    ?expr cdm:expression_uses_language <{_language_uri(lang)}> .
    ?expr cdm:expression_title ?title .
  }}
  {type_clause}
  {since_clause}
}}
ORDER BY DESC(?date)
{_limit_offset(limit, offset)}
"""
    return _with_prefixes(query)


def build_dossier_query(work_uri: str, *, limit: int, offset: int, lang: str = DEFAULT_LANGUAGE) -> str:
    """Build dossier expansion query."""
    query = f"""
SELECT DISTINCT ?dossier ?other ?celex ?title ?date ?type ?relationType ?direction ?predicate WHERE {{
  ?dossier cdm:dossier_contains_work <{work_uri}> .
  ?dossier cdm:dossier_contains_work ?other .
  BIND('dossier_contains_work' AS ?relationType)
  BIND('cdm:dossier_contains_work' AS ?predicate)
  BIND('incoming' AS ?direction)
  OPTIONAL {{ ?other cdm:resource_legal_id_celex ?celex }}
  OPTIONAL {{ ?other cdm:work_date_document ?date }}
  OPTIONAL {{ ?other cdm:work_has_resource-type ?type }}
  OPTIONAL {{
    ?expr cdm:expression_belongs_to_work ?other .
    ?expr cdm:expression_uses_language <{_language_uri(lang)}> .
    ?expr cdm:expression_title ?title .
  }}
}}
ORDER BY ?date
{_limit_offset(limit, offset)}
"""
    return _with_prefixes(query)


def build_deadlines_query(work_uri: str, *, limit: int, offset: int) -> str:
    """Build deadlines query."""
    query = f"""
SELECT DISTINCT ?other ?celex ?date ?relationType ?direction ?predicate WHERE {{
  BIND(<{work_uri}> AS ?other)
  OPTIONAL {{ ?other cdm:resource_legal_id_celex ?celex }}
  {{
    ?other cdm:resource_legal_date_deadline ?date .
    BIND('deadline' AS ?relationType)
    BIND('cdm:resource_legal_date_deadline' AS ?predicate)
  }} UNION {{
    ?other cdm:resource_legal_date_entry-into-force ?date .
    BIND('entry_into_force' AS ?relationType)
    BIND('cdm:resource_legal_date_entry-into-force' AS ?predicate)
  }} UNION {{
    ?other cdm:directive_date_transposition ?date .
    BIND('directive_transposition' AS ?relationType)
    BIND('cdm:directive_date_transposition' AS ?predicate)
  }}
  BIND('outgoing' AS ?direction)
}}
ORDER BY ?date
{_limit_offset(limit, offset)}
"""
    return _with_prefixes(query)


def build_ag_opinions_query(
    work_uri: str,
    *,
    since: date | datetime | str | None,
    limit: int,
    offset: int,
    lang: str = DEFAULT_LANGUAGE,
) -> str:
    """Build advocate-general opinions query."""
    since_clause = _since_filter("date", since)
    query = f"""
SELECT DISTINCT ?opinion ?celex ?title ?date ?type ?direction ?relationType ?predicate WHERE {{
  ?case cdm:case-law_interpretes_resource_legal <{work_uri}> .
  ?case cdm:case-law_has_conclusions_opinion_advocate-general ?opinion .
  BIND(?opinion AS ?other)
  BIND('incoming' AS ?direction)
  BIND('ag_opinion' AS ?relationType)
  BIND('cdm:case-law_has_conclusions_opinion_advocate-general' AS ?predicate)
  OPTIONAL {{ ?opinion cdm:resource_legal_id_celex ?celex }}
  OPTIONAL {{ ?opinion cdm:work_date_document ?date }}
  OPTIONAL {{ ?opinion cdm:work_has_resource-type ?type }}
  OPTIONAL {{
    ?expr cdm:expression_belongs_to_work ?opinion .
    ?expr cdm:expression_uses_language <{_language_uri(lang)}> .
    ?expr cdm:expression_title ?title .
  }}
  {since_clause}
}}
ORDER BY DESC(?date)
{_limit_offset(limit, offset)}
"""
    return _with_prefixes(query)


def build_national_decisions_query(
    celex: str,
    *,
    since: date | datetime | str | None,
    limit: int,
    offset: int,
    lang: str = DEFAULT_LANGUAGE,
) -> str:
    """Build national court decisions query by CELEX reference string."""
    since_clause = _since_filter("date", since)
    token = _quote_literal(celex.upper())
    dec_nc_uri = _resource_type_uri("DEC_NC")
    query = f"""
SELECT DISTINCT ?other ?celex ?title ?date ?type ?direction ?relationType ?predicate WHERE {{
  ?other cdm:work_has_resource-type <{dec_nc_uri}> .
  ?other cdm:case-law_national_act_reference_european ?ref .
  FILTER(CONTAINS(UCASE(STR(?ref)), {token}))
  BIND('incoming' AS ?direction)
  BIND('national_decision_reference' AS ?relationType)
  BIND('cdm:case-law_national_act_reference_european' AS ?predicate)
  OPTIONAL {{ ?other cdm:resource_legal_id_celex ?celex }}
  OPTIONAL {{ ?other cdm:work_date_document ?date }}
  OPTIONAL {{ ?other cdm:work_has_resource-type ?type }}
  OPTIONAL {{
    ?expr cdm:expression_belongs_to_work ?other .
    ?expr cdm:expression_uses_language <{_language_uri(lang)}> .
    ?expr cdm:expression_title ?title .
  }}
  {since_clause}
}}
ORDER BY DESC(?date)
{_limit_offset(limit, offset)}
"""
    return _with_prefixes(query)


def build_article_annotations_query(work_uri: str, *, limit: int, offset: int) -> str:
    """Build OWL annotation-level relation query."""
    query = f"""
SELECT DISTINCT ?other ?predicate ?relationType ?direction ?date WHERE {{
  ?annotation owl:annotatedTarget <{work_uri}> .
  ?annotation owl:annotatedSource ?other .
  ?annotation owl:annotatedProperty ?annProp .
  BIND(STR(?annProp) AS ?predicate)
  BIND('article_annotation' AS ?relationType)
  BIND('incoming' AS ?direction)
  OPTIONAL {{ ?other cdm:work_date_document ?date }}
}}
ORDER BY DESC(?date)
{_limit_offset(limit, offset)}
"""
    return _with_prefixes(query)


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
        lit = _quote_literal(tag)
        tag_filters.append(
            f"CONTAINS(LCASE(STR(?concept)), LCASE({lit})) || CONTAINS(LCASE(STR(?conceptLabel)), LCASE({lit}))"
        )
    filter_clause = " || ".join(tag_filters) if tag_filters else "true"
    since_clause = _since_filter("date", since)
    type_clause = ""
    if resource_type is not None:
        type_clause = f"?work cdm:work_has_resource-type <{_resource_type_uri(resource_type)}> ."

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
    ?expr cdm:expression_uses_language <{_language_uri(lang)}> .
    ?expr cdm:expression_title ?title .
  }}
  {type_clause}
  {since_clause}
}}
ORDER BY DESC(?date)
{_limit_offset(limit, offset)}
"""
    return _with_prefixes(query)


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
        lit = _quote_literal(code)
        code_filters.append(
            f"CONTAINS(LCASE(STR(?concept)), LCASE({lit})) || CONTAINS(LCASE(STR(?conceptLabel)), LCASE({lit}))"
        )
    filter_clause = " || ".join(code_filters) if code_filters else "true"
    since_clause = _since_filter("date", since)
    type_clause = ""
    if resource_type is not None:
        type_clause = f"?work cdm:work_has_resource-type <{_resource_type_uri(resource_type)}> ."

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
    ?expr cdm:expression_uses_language <{_language_uri(lang)}> .
    ?expr cdm:expression_title ?title .
  }}
  {type_clause}
  {since_clause}
}}
ORDER BY DESC(?date)
{_limit_offset(limit, offset)}
"""
    return _with_prefixes(query)


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
    keyword_literal = _quote_literal(keyword)
    since_clause = _since_filter("date", since)
    type_clause = ""
    if resource_type is not None:
        type_clause = f"?work cdm:work_has_resource-type <{_resource_type_uri(resource_type)}> ."

    query = f"""
SELECT DISTINCT ?work ?celex ?title ?date ?type WHERE {{
  ?expr cdm:expression_belongs_to_work ?work .
  ?expr cdm:expression_uses_language <{_language_uri(lang)}> .
  ?expr cdm:expression_title ?title .
  FILTER(CONTAINS(LCASE(STR(?title)), LCASE({keyword_literal})))
  OPTIONAL {{ ?work cdm:resource_legal_id_celex ?celex }}
  OPTIONAL {{ ?work cdm:work_date_document ?date }}
  OPTIONAL {{ ?work cdm:work_has_resource-type ?type }}
  {type_clause}
  {since_clause}
}}
ORDER BY DESC(?date)
{_limit_offset(limit, offset)}
"""
    return _with_prefixes(query)


def build_search_communications_query(
    dg: str,
    *,
    since: date | datetime | str | None,
    limit: int,
    offset: int,
    lang: str = DEFAULT_LANGUAGE,
) -> str:
    """Build search query for Commission communications by responsible service."""
    dg_literal = _quote_literal(dg)
    since_clause = _since_filter("date", since)
    communic_uri = _resource_type_uri("COMMUNIC")

    query = f"""
SELECT DISTINCT ?work ?celex ?title ?date ?type WHERE {{
  ?work cdm:work_has_resource-type <{communic_uri}> .
  OPTIONAL {{ ?work cdm:resource_legal_service_responsible ?service }}
  FILTER(CONTAINS(UCASE(STR(?service)), UCASE({dg_literal})))
  OPTIONAL {{ ?work cdm:resource_legal_id_celex ?celex }}
  OPTIONAL {{ ?work cdm:work_date_document ?date }}
  OPTIONAL {{ ?work cdm:work_has_resource-type ?type }}
  OPTIONAL {{
    ?expr cdm:expression_belongs_to_work ?work .
    ?expr cdm:expression_uses_language <{_language_uri(lang)}> .
    ?expr cdm:expression_title ?title .
  }}
  {since_clause}
}}
ORDER BY DESC(?date)
{_limit_offset(limit, offset)}
"""
    return _with_prefixes(query)


def build_find_eurovoc_concept_query(label: str, *, limit: int, offset: int) -> str:
    """Build EuroVoc concept lookup query."""
    label_literal = _quote_literal(label)
    query = f"""
SELECT DISTINCT ?concept ?label WHERE {{
  ?concept skos:prefLabel ?label .
  FILTER(LANG(?label) = 'en' || LANG(?label) = '')
  FILTER(CONTAINS(LCASE(STR(?label)), LCASE({label_literal})))
}}
ORDER BY ?label
{_limit_offset(limit, offset)}
"""
    return _with_prefixes(query)


def build_summary_lookup_query(work_uri: str) -> str:
    """Build query resolving legissum summary URI for a work URI."""
    query = f"""
SELECT DISTINCT ?summary WHERE {{
  {{ ?summary cdm:summary_summarizes_work <{work_uri}> . }}
  UNION
  {{ ?summary cdm:summary_legislation_eu_summarizes_resource_legal <{work_uri}> . }}
}}
LIMIT 1
"""
    return _with_prefixes(query)
