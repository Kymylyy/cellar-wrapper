"""Shared serialization helpers for domain errors."""

from __future__ import annotations

import json
from typing import Any

from cellar_wrapper.errors import (
    CellarError,
    CellarHTTPError,
    CellarInternalError,
    CellarNotFoundError,
    CellarParseError,
    CellarRateLimitError,
    CellarSPARQLError,
)
from cellar_wrapper.serialization import to_jsonable


def cellar_error_details(exc: CellarError) -> dict[str, Any]:
    """Return JSON-serializable details payload for known domain errors."""
    details: dict[str, Any] = {}
    if isinstance(exc, CellarHTTPError):
        details = {
            "status_code": exc.status_code,
            "url": exc.url,
            "body_excerpt": exc.body_excerpt,
            "details": exc.details,
        }
        if isinstance(exc, CellarRateLimitError):
            details["retry_after"] = exc.retry_after
            details["retry_after_seconds"] = exc.retry_after_seconds
    elif isinstance(exc, CellarSPARQLError):
        details = {
            "query": exc.query,
            "response_excerpt": exc.response_excerpt,
            "details": exc.details,
        }
    elif isinstance(exc, CellarNotFoundError):
        details = {"details": exc.details}
    elif isinstance(exc, CellarParseError):
        details = {"details": exc.details}
    elif isinstance(exc, CellarInternalError):
        details = exc.details
    return details


def _safe_repr(value: Any) -> str:
    try:
        return repr(value)
    except Exception:  # pragma: no cover - extreme defensive fallback
        return f"<unrepresentable {type(value).__name__}>"


def _json_default(value: Any) -> Any:
    converted = to_jsonable(value)
    if converted is value:
        return _safe_repr(value)
    return converted


def _safe_json_dumps(value: Any) -> str:
    try:
        return json.dumps(
            to_jsonable(value),
            ensure_ascii=False,
            sort_keys=True,
            default=_json_default,
        )
    except Exception:  # pragma: no cover - defensive guard
        return json.dumps(
            {"unserializable_details": _safe_repr(value)},
            ensure_ascii=False,
            sort_keys=True,
        )


def format_cellar_error(exc: CellarError) -> str:
    """Format domain errors for plain-text channels (for example MCP ToolError)."""
    details = cellar_error_details(exc)
    if not details:
        return f"{type(exc).__name__}: {exc}"
    return f"{type(exc).__name__}: {exc} | details={_safe_json_dumps(details)}"
