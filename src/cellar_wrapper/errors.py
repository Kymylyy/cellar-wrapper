"""Custom exception hierarchy for CELLAR wrapper."""

from __future__ import annotations

from typing import Any


class CellarError(Exception):
    """Base class for all wrapper errors."""


class CellarValidationError(CellarError):
    """Raised when input validation fails."""


class CellarHTTPError(CellarError):
    """Raised when HTTP response is not successful."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        url: str,
        body_excerpt: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.url = url
        self.body_excerpt = body_excerpt
        self.details = details or {}


class CellarRateLimitError(CellarHTTPError):
    """Raised when the endpoint responds with HTTP 429."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        url: str,
        retry_after: str | None,
        body_excerpt: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message,
            status_code=status_code,
            url=url,
            body_excerpt=body_excerpt,
            details=details,
        )
        self.retry_after = retry_after


class CellarSPARQLError(CellarError):
    """Raised when a SPARQL query fails or response is invalid."""


class CellarParseError(CellarError):
    """Raised when parsing endpoint payload fails."""


class CellarNotFoundError(CellarError):
    """Raised when CELEX/work URI cannot be found."""
