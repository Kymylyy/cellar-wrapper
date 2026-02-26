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


class CellarTimeoutError(CellarHTTPError):
    """Raised when HTTP request times out."""


class CellarRateLimitError(CellarHTTPError):
    """Raised when the endpoint responds with HTTP 429."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        url: str,
        retry_after: str | None,
        retry_after_seconds: int | None = None,
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
        self.retry_after_seconds = retry_after_seconds


class CellarSPARQLError(CellarError):
    """Raised when a SPARQL query fails or response is invalid."""

    def __init__(
        self,
        message: str,
        *,
        query: str | None = None,
        response_excerpt: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.query = query
        self.response_excerpt = response_excerpt
        self.details = details or {}


class CellarParseError(CellarError):
    """Raised when parsing endpoint payload fails."""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


class CellarInternalError(CellarError):
    """Raised when CLI catches an unexpected runtime exception."""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


class CellarNotFoundError(CellarError):
    """Raised when CELEX/work URI cannot be found."""
