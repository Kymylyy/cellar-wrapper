"""Common SPARQL helpers and shared types."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from urllib.parse import urlparse

from cellar_wrapper.constants import (
    DEFAULT_LIMIT,
    DEFAULT_OFFSET,
    LANGUAGE_URI_TEMPLATE,
    PREDICATES,
    RESOURCE_TYPE_URI_TEMPLATE,
    SPARQL_PREFIXES,
)
from cellar_wrapper.date_utils import parse_iso_date_or_datetime

LANGUAGE_TOKEN_RE = re.compile(r"^[A-Za-z]{3}$")
RESOURCE_TYPE_TOKEN_RE = re.compile(r"^[A-Z_]+$")
SPARQL_VAR_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


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


def safe_iri(value: str, *, field: str) -> str:
    """Validate and normalize an IRI used inside `<...>`."""
    candidate = value.strip()
    if not candidate:
        raise ValueError(f"{field} cannot be empty")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in candidate):
        raise ValueError(f"Invalid IRI for {field}: contains control characters")
    if any(ch.isspace() for ch in candidate):
        raise ValueError(f"Invalid IRI for {field}: contains whitespace")
    if any(ch in candidate for ch in "<>{}\"'`"):
        raise ValueError(f"Invalid IRI for {field}: {value!r}")
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Invalid IRI for {field}: {value!r}")
    return candidate


def language_uri(lang: str) -> str:
    """Build language authority URI."""
    token = lang.strip().upper()
    if not LANGUAGE_TOKEN_RE.fullmatch(token):
        raise ValueError(f"Invalid language token: {lang!r}")
    return safe_iri(LANGUAGE_URI_TEMPLATE.format(lang=token), field="language_uri")


def resource_type_uri(resource_type: str) -> str:
    """Build resource-type authority URI."""
    token = resource_type.strip().upper()
    if not RESOURCE_TYPE_TOKEN_RE.fullmatch(token):
        raise ValueError(f"Invalid resource_type token: {resource_type!r}")
    return safe_iri(
        RESOURCE_TYPE_URI_TEMPLATE.format(resource_type=token),
        field="resource_type_uri",
    )


def with_prefixes(body: str) -> str:
    """Prepend common prefixes to a query body."""
    return f"{SPARQL_PREFIXES}\n\n{body.strip()}"


def limit_offset(limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET) -> str:
    """Render LIMIT/OFFSET clause."""
    return f"LIMIT {limit}\nOFFSET {offset}"


def _normalize_datetime_lexical(dt: datetime) -> str:
    """Serialize datetime to a canonical UTC lexical representation."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    dt_utc = dt.astimezone(UTC).replace(microsecond=0)
    return dt_utc.isoformat().replace("+00:00", "Z")


def _normalize_date_bound_datetime(value: date | datetime | str, *, field_name: str) -> datetime:
    """Normalize date-like input to a UTC datetime for filtering."""
    if isinstance(value, datetime):
        normalized = value
    elif isinstance(value, date):
        normalized = datetime.combine(value, time.min, tzinfo=UTC)
    else:
        candidate = value.strip()
        if not candidate:
            raise ValueError(f"{field_name} cannot be empty")
        try:
            parsed = parse_iso_date_or_datetime(candidate)
        except ValueError as exc:
            raise ValueError(f"Invalid {field_name} value (expected ISO date/datetime): {value!r}") from exc
        if isinstance(parsed, datetime):
            normalized = parsed
        else:
            normalized = datetime.combine(parsed, time.min, tzinfo=UTC)

    if normalized.tzinfo is None:
        normalized = normalized.replace(tzinfo=UTC)
    return normalized.astimezone(UTC).replace(microsecond=0)


def date_bounds_filter(
    var_name: str,
    *,
    since: date | datetime | str | None = None,
    to: date | datetime | str | None = None,
    include_undated: bool = False,
) -> str:
    """Render strict date-bound filter for date-like columns."""
    if since is None and to is None:
        return ""
    if not SPARQL_VAR_RE.fullmatch(var_name):
        raise ValueError(f"Invalid SPARQL variable name: {var_name!r}")

    normalized_since: datetime | None = None
    normalized_to: datetime | None = None
    comparisons: list[str] = []
    if since is not None:
        normalized_since = _normalize_date_bound_datetime(since, field_name="since")
        since_literal = quote_literal(_normalize_datetime_lexical(normalized_since))
        comparisons.append(f"?{var_name} > {since_literal}^^xsd:dateTime")
    if to is not None:
        normalized_to = _normalize_date_bound_datetime(to, field_name="to")
        to_literal = quote_literal(_normalize_datetime_lexical(normalized_to))
        comparisons.append(f"?{var_name} < {to_literal}^^xsd:dateTime")
    if normalized_since is not None and normalized_to is not None and normalized_since > normalized_to:
        raise ValueError("since cannot be later than to")

    comparison = " && ".join(comparisons)
    if len(comparisons) > 1:
        comparison = f"({comparison})"
    if include_undated:
        return f"FILTER(!BOUND(?{var_name}) || {comparison})"
    return f"FILTER(BOUND(?{var_name}) && {comparison})"


def since_filter(
    var_name: str,
    since: date | datetime | str | None,
    *,
    include_undated: bool = False,
) -> str:
    """Backward-compatible wrapper for a lower date bound."""
    return date_bounds_filter(var_name, since=since, include_undated=include_undated)


def resource_type_clause(resource_type: str | None) -> str:
    """Render optional resource-type filter clause."""
    if resource_type is None:
        return ""
    return (
        f"?other {PREDICATES['work_has_resource_type']} "
        f"<{resource_type_uri(resource_type)}> ."
    )
