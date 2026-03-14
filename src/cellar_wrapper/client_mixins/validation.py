"""Validation and normalization helpers for client mixins."""

from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import UTC, date, datetime, time

from cellar_wrapper.constants import MAX_LIMIT
from cellar_wrapper.date_utils import parse_iso_date_or_datetime
from cellar_wrapper.errors import CellarValidationError

CELEX_RE = re.compile(r"^[0-9A-Z()_\-]{5,40}$")
LANG_RE = re.compile(r"^[a-zA-Z]{3}$")
RESOURCE_TYPE_RE = re.compile(r"^[A-Z_]+$")
COUNTRY_RE = re.compile(r"^[A-Z]{3}$")
DIRECTION_VALUES = {"incoming", "outgoing", "both"}


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


def normalize_resource_types(resource_types: Sequence[str] | None) -> list[str] | None:
    if resource_types is None:
        return None

    normalized_values: list[str] = []
    seen_values: set[str] = set()
    for resource_type in resource_types:
        normalized = resource_type.strip().upper()
        if not RESOURCE_TYPE_RE.fullmatch(normalized):
            raise CellarValidationError(f"Invalid resource_type: {resource_type!r}")
        if normalized in seen_values:
            continue
        seen_values.add(normalized)
        normalized_values.append(normalized)

    if not normalized_values:
        raise CellarValidationError("resource_types cannot be empty")
    return normalized_values


def normalize_country(country: str | None) -> str | None:
    if country is None:
        return None
    normalized = country.strip().upper()
    if not COUNTRY_RE.fullmatch(normalized):
        raise CellarValidationError(f"Invalid country code (expected ISO-3): {country!r}")
    return normalized


def normalize_direction(direction: str | None) -> str | None:
    if direction is None:
        return None
    normalized = direction.strip().lower()
    if normalized not in DIRECTION_VALUES:
        raise CellarValidationError(f"Invalid direction: {direction!r}")
    return normalized


def _normalize_date_bound(value: date | datetime | str, *, field_name: str) -> datetime:
    if isinstance(value, datetime):
        normalized = value
    elif isinstance(value, date):
        normalized = datetime.combine(value, time.min, tzinfo=UTC)
    else:
        candidate = value.strip()
        if not candidate:
            raise CellarValidationError(f"{field_name} cannot be empty")
        try:
            parsed = parse_iso_date_or_datetime(candidate)
        except ValueError as exc:
            raise CellarValidationError(
                f"Invalid {field_name} value (expected ISO date/datetime): {value!r}"
            ) from exc
        if isinstance(parsed, datetime):
            normalized = parsed
        else:
            normalized = datetime.combine(parsed, time.min, tzinfo=UTC)

    if normalized.tzinfo is None:
        normalized = normalized.replace(tzinfo=UTC)
    return normalized.astimezone(UTC).replace(microsecond=0)


def coerce_date_bound(value: date | datetime | str | None, *, field_name: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()

    candidate = value.strip()
    _ = _normalize_date_bound(candidate, field_name=field_name)
    return candidate


def coerce_since(since: date | datetime | str | None) -> str | None:
    return coerce_date_bound(since, field_name="since")


def coerce_to(to: date | datetime | str | None) -> str | None:
    return coerce_date_bound(to, field_name="to")


def validate_date_range(
    since: date | datetime | str | None,
    to: date | datetime | str | None,
) -> None:
    if since is None or to is None:
        return
    if _normalize_date_bound(since, field_name="since") > _normalize_date_bound(
        to,
        field_name="to",
    ):
        raise CellarValidationError("since cannot be later than to")


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
