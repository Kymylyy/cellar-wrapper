"""SPARQL builders for relations, lifecycle and case-law links."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime

from cellar_wrapper.constants import DEFAULT_LANGUAGE, PREDICATES

from .common import (
    PredicateSpec,
    date_bounds_filter,
    language_uri,
    limit_offset,
    quote_literal,
    resource_type_uri,
    safe_iri,
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
    to: date | datetime | str | None = None,
    lang: str = DEFAULT_LANGUAGE,
    include_undated: bool = True,
    include_origin_country: bool = False,
    include_implemented_by_country: bool = False,
) -> str:
    """Build generic relation query over one or more predicates."""
    if not predicates:
        raise ValueError("predicates cannot be empty")
    if direction not in {"incoming", "outgoing", "both"}:
        raise ValueError(f"Unsupported direction: {direction}")
    work_iri = safe_iri(work_uri, field="work_uri")
    lang_iri = language_uri(lang)
    unions: list[str] = []
    for spec in predicates:
        if direction in {"incoming", "both"}:
            unions.append(
                f"""
  {{
    ?other {spec.iri} <{work_iri}> .
    BIND({quote_literal("incoming")} AS ?direction)
    BIND({quote_literal(spec.relation_type)} AS ?relationType)
    BIND({quote_literal(spec.iri)} AS ?predicate)
  }}
""".strip()
            )
        if direction in {"outgoing", "both"}:
            unions.append(
                f"""
  {{
    <{work_iri}> {spec.iri} ?other .
    BIND({quote_literal("outgoing")} AS ?direction)
    BIND({quote_literal(spec.relation_type)} AS ?relationType)
    BIND({quote_literal(spec.iri)} AS ?predicate)
  }}
""".strip()
            )

    union_block = " UNION\n".join(unions)

    extra_select_vars: list[str] = []
    optional_blocks: list[str] = []
    if include_origin_country:
        extra_select_vars.append("?originCountry")
        optional_blocks.append(
            f'OPTIONAL {{ ?other {PREDICATES["case_law_originates_in_country"]} ?originCountry }}'
        )
    if include_implemented_by_country:
        extra_select_vars.append("?implementedByCountry")
        optional_blocks.append(
            f'OPTIONAL {{ ?other {PREDICATES["implemented_by_country"]} ?implementedByCountry }}'
        )
    extra_select = (" " + " ".join(extra_select_vars)) if extra_select_vars else ""
    extra_optional = ("\n  " + "\n  ".join(optional_blocks)) if optional_blocks else ""
    if resource_type is None:
        type_clause = f'OPTIONAL {{ ?other {PREDICATES["work_has_resource_type"]} ?type }}'
    else:
        type_clause = (
            f'?other {PREDICATES["work_has_resource_type"]} ?type .\n'
            f'  FILTER(?type = <{resource_type_uri(resource_type)}>)'
        )

    query = f"""
SELECT DISTINCT ?other ?celex ?title ?date ?type ?direction ?relationType ?predicate ?ecli ?courtFormation ?advocateGeneral{extra_select} WHERE {{
{union_block}
  OPTIONAL {{ ?other {PREDICATES["resource_legal_id_celex"]} ?celex }}
  OPTIONAL {{ ?other {PREDICATES["work_date_document"]} ?date }}
  {type_clause}
  OPTIONAL {{ ?other {PREDICATES["case_law_ecli"]} ?ecli }}
  OPTIONAL {{ ?other {PREDICATES["case_law_delivered_by_court_formation"]} ?courtFormation }}
  OPTIONAL {{ ?other {PREDICATES["case_law_delivered_by_advocate_general"]} ?advocateGeneral }}
  {extra_optional}
  OPTIONAL {{
    ?expr {PREDICATES["expression_belongs_to_work"]} ?other .
    ?expr {PREDICATES["expression_uses_language"]} <{lang_iri}> .
    ?expr {PREDICATES["expression_title"]} ?title .
  }}
  {date_bounds_filter("date", since=since, to=to, include_undated=include_undated)}
}}
ORDER BY DESC(?date)
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


def build_dossier_query(work_uri: str, *, limit: int, offset: int, lang: str = DEFAULT_LANGUAGE) -> str:
    """Build dossier expansion query."""
    work_iri = safe_iri(work_uri, field="work_uri")
    lang_iri = language_uri(lang)
    query = f"""
SELECT DISTINCT ?dossier ?procedureCode ?procedureType ?statusAdopted ?statusPending ?statusWithdrawn ?producesAct ?producesActCelex ?other ?celex ?title ?date ?type ?relationType ?direction ?predicate WHERE {{
  {{
    SELECT DISTINCT ?dossier ?other ?date WHERE {{
      ?dossier {PREDICATES["dossier_contains_work"]} <{work_iri}> .
      ?dossier {PREDICATES["dossier_contains_work"]} ?other .
      FILTER(?other != <{work_iri}>)
      OPTIONAL {{ ?other {PREDICATES["work_date_document"]} ?date }}
    }}
    ORDER BY ?date ?other ?dossier
    {limit_offset(limit, offset)}
  }}
  BIND({quote_literal("dossier_contains_work")} AS ?relationType)
  BIND({quote_literal(PREDICATES["dossier_contains_work"])} AS ?predicate)
  BIND({quote_literal("incoming")} AS ?direction)
  OPTIONAL {{
    ?dossier {PREDICATES["procedure_code_interinstitutional_reference_procedure"]} ?procedureCode
  }}
  OPTIONAL {{ ?dossier {PREDICATES["procedure_code_interinstitutional_has_type"]} ?procedureType }}
  OPTIONAL {{ ?dossier {PREDICATES["dossier_adopted_proposal"]} ?statusAdopted }}
  OPTIONAL {{ ?dossier {PREDICATES["dossier_pending_proposal"]} ?statusPending }}
  OPTIONAL {{ ?dossier {PREDICATES["dossier_withdrawn_proposal"]} ?statusWithdrawn }}
  OPTIONAL {{
    ?dossier {PREDICATES["dossier_produces_resource_legal"]} ?producesAct .
    OPTIONAL {{ ?producesAct {PREDICATES["resource_legal_id_celex"]} ?producesActCelex }}
  }}
  OPTIONAL {{ ?other {PREDICATES["resource_legal_id_celex"]} ?celex }}
  OPTIONAL {{ ?other {PREDICATES["work_has_resource_type"]} ?type }}
  OPTIONAL {{
    ?expr {PREDICATES["expression_belongs_to_work"]} ?other .
    ?expr {PREDICATES["expression_uses_language"]} <{lang_iri}> .
    ?expr {PREDICATES["expression_title"]} ?title .
  }}
}}
ORDER BY ?date ?other ?dossier
"""
    return with_prefixes(query)


def build_deadlines_query(work_uri: str, *, limit: int, offset: int) -> str:
    """Build deadlines query."""
    work_iri = safe_iri(work_uri, field="work_uri")
    query = f"""
SELECT DISTINCT ?other ?celex ?date ?relationType ?direction ?predicate WHERE {{
  BIND(<{work_iri}> AS ?other)
  OPTIONAL {{ ?other {PREDICATES["resource_legal_id_celex"]} ?celex }}
  {{
    ?other {PREDICATES["deadline"]} ?date .
    BIND({quote_literal("deadline")} AS ?relationType)
    BIND({quote_literal(PREDICATES["deadline"])} AS ?predicate)
  }} UNION {{
    ?other {PREDICATES["entry_into_force"]} ?date .
    BIND({quote_literal("entry_into_force")} AS ?relationType)
    BIND({quote_literal(PREDICATES["entry_into_force"])} AS ?predicate)
  }} UNION {{
    ?other {PREDICATES["directive_transposition"]} ?date .
    BIND({quote_literal("directive_transposition")} AS ?relationType)
    BIND({quote_literal(PREDICATES["directive_transposition"])} AS ?predicate)
  }}
  BIND({quote_literal("outgoing")} AS ?direction)
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
    to: date | datetime | str | None = None,
    lang: str = DEFAULT_LANGUAGE,
) -> str:
    """Build advocate-general opinions query."""
    work_iri = safe_iri(work_uri, field="work_uri")
    lang_iri = language_uri(lang)
    query = f"""
SELECT DISTINCT ?opinion ?celex ?title ?date ?type ?direction ?relationType ?predicate WHERE {{
  ?case {PREDICATES["cjeu_interprets"]} <{work_iri}> .
  ?case {PREDICATES["ag_opinion"]} ?opinion .
  BIND(?opinion AS ?other)
  BIND({quote_literal("incoming")} AS ?direction)
  BIND({quote_literal("ag_opinion")} AS ?relationType)
  BIND({quote_literal(PREDICATES["ag_opinion"])} AS ?predicate)
  OPTIONAL {{ ?opinion {PREDICATES["resource_legal_id_celex"]} ?celex }}
  OPTIONAL {{ ?opinion {PREDICATES["work_date_document"]} ?date }}
  OPTIONAL {{ ?opinion {PREDICATES["work_has_resource_type"]} ?type }}
  OPTIONAL {{
    ?expr {PREDICATES["expression_belongs_to_work"]} ?opinion .
    ?expr {PREDICATES["expression_uses_language"]} <{lang_iri}> .
    ?expr {PREDICATES["expression_title"]} ?title .
  }}
  {date_bounds_filter("date", since=since, to=to, include_undated=True)}
}}
ORDER BY DESC(?date)
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


def build_national_decisions_query(
    celex: str,
    *,
    since: date | datetime | str | None,
    country: str | None = None,
    limit: int,
    offset: int,
    to: date | datetime | str | None = None,
    lang: str = DEFAULT_LANGUAGE,
) -> str:
    """Build national court decisions query by CELEX reference string."""
    dec_nc_uri = resource_type_uri("DEC_NC")
    lang_iri = language_uri(lang)
    country_filter = ""
    if country is not None:
        country_filter = (
            f"FILTER(CONTAINS(UCASE(STR(?originCountry)), {quote_literal(country.upper())}))"
        )
    query = f"""
SELECT DISTINCT ?other ?celex ?title ?date ?type ?direction ?relationType ?predicate ?originCountry WHERE {{
  ?other {PREDICATES["work_has_resource_type"]} <{dec_nc_uri}> .
  ?other {PREDICATES["national_act_reference"]} ?ref .
  FILTER(CONTAINS(UCASE(STR(?ref)), {quote_literal(celex.upper())}))
  BIND({quote_literal("incoming")} AS ?direction)
  BIND({quote_literal("national_decision_reference")} AS ?relationType)
  BIND({quote_literal(PREDICATES["national_act_reference"])} AS ?predicate)
  OPTIONAL {{ ?other {PREDICATES["resource_legal_id_celex"]} ?celex }}
  OPTIONAL {{ ?other {PREDICATES["work_date_document"]} ?date }}
  OPTIONAL {{ ?other {PREDICATES["work_has_resource_type"]} ?type }}
  OPTIONAL {{ ?other {PREDICATES["case_law_originates_in_country"]} ?originCountry }}
  OPTIONAL {{
    ?expr {PREDICATES["expression_belongs_to_work"]} ?other .
    ?expr {PREDICATES["expression_uses_language"]} <{lang_iri}> .
    ?expr {PREDICATES["expression_title"]} ?title .
  }}
  {country_filter}
  {date_bounds_filter("date", since=since, to=to, include_undated=True)}
}}
ORDER BY DESC(?date)
{limit_offset(limit, offset)}
"""
    return with_prefixes(query)


def build_article_annotations_query(work_uri: str, *, limit: int, offset: int) -> str:
    """Build OWL annotation-level relation query."""
    work_iri = safe_iri(work_uri, field="work_uri")
    query = f"""
SELECT DISTINCT ?other ?predicate ?relationType ?direction ?date ?annotation ?article ?paragraph ?subparagraph ?point ?commentOnLegalBasis WHERE {{
  ?annotation owl:annotatedTarget <{work_iri}> .
  ?annotation owl:annotatedSource ?other .
  ?annotation owl:annotatedProperty ?annProp .
  BIND(STR(?annProp) AS ?predicate)
  BIND({quote_literal("article_annotation")} AS ?relationType)
  BIND({quote_literal("incoming")} AS ?direction)
  OPTIONAL {{ ?other {PREDICATES["work_date_document"]} ?date }}
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
