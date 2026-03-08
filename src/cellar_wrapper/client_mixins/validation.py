"""Validation and normalization helpers for client mixins."""

from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import date, datetime

from cellar_wrapper.constants import MAX_LIMIT
from cellar_wrapper.date_utils import parse_iso_date_or_datetime
from cellar_wrapper.errors import CellarValidationError

CELEX_RE = re.compile(r"^[0-9A-Z()_\-]{5,40}$")
LANG_RE = re.compile(r"^[a-zA-Z]{3}$")
RESOURCE_TYPE_RE = re.compile(r"^[A-Z_]+$")
COUNTRY_RE = re.compile(r"^[A-Z]{3}$")


def normalize_celex(celex: str) -> str:
    normalized = celex.strip().upper()
    if not CELEX_RE.fullmatch(normalized):
        raise CellarValidationError(f"Invalid CELEX identifier: {celex!r}")
    return normalized


def normalize_lang(lang: str) -> str:
    normalized = lang.strip().lower()
    if not LANG_RE.fullmatch(normalized):
        raise CellarValidationError(f"Invalid language code: {lang!r}")
    return normalized


def normalize_resource_type(resource_type: str | None) -> str | None:
    if resource_type is None:
        return None
    normalized = resource_type.strip().upper()
    if not RESOURCE_TYPE_RE.fullmatch(normalized):
        raise CellarValidationError(f"Invalid resource_type: {resource_type!r}")
    return normalized


def normalize_country(country: str | None) -> str | None:
    if country is None:
        return None
    normalized = country.strip().upper()
    if not COUNTRY_RE.fullmatch(normalized):
        raise CellarValidationError(f"Invalid country code (expected ISO-3): {country!r}")
    return normalized


def coerce_since(since: date | datetime | str | None) -> str | None:
    if since is None:
        return None
    if isinstance(since, datetime):
        return since.isoformat()
    if isinstance(since, date):
        return since.isoformat()

    candidate = since.strip()
    try:
        parse_iso_date_or_datetime(candidate)
        return candidate
    except ValueError as exc:
        raise CellarValidationError(
            f"Invalid since value (expected ISO date/datetime): {since!r}"
        ) from exc


def validate_pagination(limit: int, offset: int) -> None:
    if limit <= 0:
        raise CellarValidationError("limit must be > 0")
    if limit > MAX_LIMIT:
        raise CellarValidationError(f"limit cannot exceed {MAX_LIMIT}")
    if offset < 0:
        raise CellarValidationError("offset cannot be negative")


def normalize_non_empty_values(values: Sequence[str], *, field_name: str = "values") -> list[str]:
    normalized = [item.strip() for item in values if item.strip()]
    if not normalized:
        raise CellarValidationError(f"{field_name} cannot be empty")
    return normalized


def dedupe_non_empty_casefold(values: Sequence[str]) -> list[str]:
    unique_values: list[str] = []
    seen_values: set[str] = set()
    for value in values:
        normalized = value.strip()
        if not normalized:
            continue
        dedupe_key = normalized.casefold()
        if dedupe_key in seen_values:
            continue
        seen_values.add(dedupe_key)
        unique_values.append(normalized)
    return unique_values
