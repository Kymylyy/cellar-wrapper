"""Common SPARQL helpers and shared types."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from cellar_wrapper.constants import (
    DEFAULT_LIMIT,
    DEFAULT_OFFSET,
    LANGUAGE_URI_TEMPLATE,
    PREDICATES,
    RESOURCE_TYPE_URI_TEMPLATE,
    SPARQL_PREFIXES,
)


@dataclass(frozen=True)
class PredicateSpec:
    """Predicate with human relation label."""

    iri: str
    relation_type: str


def quote_literal(value: str) -> str:
    """Escape value for SPARQL single-quoted literal."""
    escaped = (
        value.replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )
    return f"'{escaped}'"


def date_literal(value: date | datetime | str) -> str:
    """Normalize date-like input to a string literal payload."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value


def language_uri(lang: str) -> str:
    """Build language authority URI."""
    return LANGUAGE_URI_TEMPLATE.format(lang=lang.upper())


def resource_type_uri(resource_type: str) -> str:
    """Build resource-type authority URI."""
    return RESOURCE_TYPE_URI_TEMPLATE.format(resource_type=resource_type)


def with_prefixes(body: str) -> str:
    """Prepend common prefixes to a query body."""
    return f"{SPARQL_PREFIXES}\n\n{body.strip()}"


def limit_offset(limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET) -> str:
    """Render LIMIT/OFFSET clause."""
    return f"LIMIT {limit}\nOFFSET {offset}"


def since_filter(var_name: str, since: date | datetime | str | None) -> str:
    """Render strict `>` filter for date-like column."""
    if since is None:
        return ""
    normalized = date_literal(since)
    literal = quote_literal(normalized)
    datatype = "xsd:dateTime" if "T" in normalized.upper() else "xsd:date"
    return f"FILTER(?{var_name} > {literal}^^{datatype})"


def resource_type_clause(resource_type: str | None) -> str:
    """Render optional resource-type filter clause."""
    if resource_type is None:
        return ""
    return f"?other {PREDICATES['work_has_resource_type']} <{resource_type_uri(resource_type)}> ."
