"""SPARQL builders for relations, lifecycle and case-law links."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime

from cellar_wrapper.constants import DEFAULT_LANGUAGE

from .common import (
    PredicateSpec,
    language_uri,
    limit_offset,
    quote_literal,
    resource_type_clause,
    resource_type_uri,
    since_filter,
    with_prefixes,
)


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
    ?expr cdm:expression_uses_language <{language_uri(lang)}> .
    ?expr cdm:expression_title ?title .
  }}
  {resource_type_clause(resource_type)}
  {since_filter("date", since)}
}}
ORDER BY DESC(?date)
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


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
    ?expr cdm:expression_uses_language <{language_uri(lang)}> .
    ?expr cdm:expression_title ?title .
  }}
}}
ORDER BY ?date
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


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
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


def build_ag_opinions_query(
    work_uri: str,
    *,
    since: date | datetime | str | None,
    limit: int,
    offset: int,
    lang: str = DEFAULT_LANGUAGE,
) -> str:
    """Build advocate-general opinions query."""
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
    ?expr cdm:expression_uses_language <{language_uri(lang)}> .
    ?expr cdm:expression_title ?title .
  }}
  {since_filter("date", since)}
}}
ORDER BY DESC(?date)
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


def build_national_decisions_query(
    celex: str,
    *,
    since: date | datetime | str | None,
    limit: int,
    offset: int,
    lang: str = DEFAULT_LANGUAGE,
) -> str:
    """Build national court decisions query by CELEX reference string."""
    dec_nc_uri = resource_type_uri("DEC_NC")
    query = f"""
SELECT DISTINCT ?other ?celex ?title ?date ?type ?direction ?relationType ?predicate WHERE {{
  ?other cdm:work_has_resource-type <{dec_nc_uri}> .
  ?other cdm:case-law_national_act_reference_european ?ref .
  FILTER(CONTAINS(UCASE(STR(?ref)), {quote_literal(celex.upper())}))
  BIND('incoming' AS ?direction)
  BIND('national_decision_reference' AS ?relationType)
  BIND('cdm:case-law_national_act_reference_european' AS ?predicate)
  OPTIONAL {{ ?other cdm:resource_legal_id_celex ?celex }}
  OPTIONAL {{ ?other cdm:work_date_document ?date }}
  OPTIONAL {{ ?other cdm:work_has_resource-type ?type }}
  OPTIONAL {{
    ?expr cdm:expression_belongs_to_work ?other .
    ?expr cdm:expression_uses_language <{language_uri(lang)}> .
    ?expr cdm:expression_title ?title .
  }}
  {since_filter("date", since)}
}}
ORDER BY DESC(?date)
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


def build_article_annotations_query(work_uri: str, *, limit: int, offset: int) -> str:
    """Build OWL annotation-level relation query."""
    query = f"""
SELECT DISTINCT ?other ?predicate ?relationType ?direction ?date ?annotation ?article ?paragraph ?subparagraph ?point ?commentOnLegalBasis WHERE {{
  ?annotation owl:annotatedTarget <{work_uri}> .
  ?annotation owl:annotatedSource ?other .
  ?annotation owl:annotatedProperty ?annProp .
  BIND(STR(?annProp) AS ?predicate)
  BIND('article_annotation' AS ?relationType)
  BIND('incoming' AS ?direction)
  OPTIONAL {{ ?other cdm:work_date_document ?date }}
  OPTIONAL {{
    ?annotation ?articlePredicate ?article .
    FILTER(REGEX(STR(?articlePredicate), "(^|[#/:])article$", "i"))
  }}
  OPTIONAL {{
    ?annotation ?paragraphPredicate ?paragraph .
    FILTER(REGEX(STR(?paragraphPredicate), "(^|[#/:])paragraph$", "i"))
  }}
  OPTIONAL {{
    ?annotation ?subparagraphPredicate ?subparagraph .
    FILTER(REGEX(STR(?subparagraphPredicate), "(^|[#/:])subparagraph$", "i"))
  }}
  OPTIONAL {{
    ?annotation ?pointPredicate ?point .
    FILTER(REGEX(STR(?pointPredicate), "(^|[#/:])point$", "i"))
  }}
  OPTIONAL {{
    ?annotation ?commentPredicate ?commentOnLegalBasis .
    FILTER(REGEX(STR(?commentPredicate), "comment_on_legal_basis$", "i"))
  }}
}}
ORDER BY DESC(?date)
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)
