"""Shared helpers for ISO date and datetime handling."""

from __future__ import annotations

from datetime import date, datetime


def parse_iso_date_or_datetime(raw: str) -> date | datetime:
    """Parse ISO date or datetime string, accepting trailing Z for UTC."""
    candidate = raw.strip()
    if not candidate:
        raise ValueError("empty date/datetime value")

    candidate_for_datetime = candidate.replace("Z", "+00:00")
    if "T" in candidate_for_datetime.upper():
        return datetime.fromisoformat(candidate_for_datetime)

    try:
        return date.fromisoformat(candidate)
    except ValueError:
        return datetime.fromisoformat(candidate_for_datetime)
