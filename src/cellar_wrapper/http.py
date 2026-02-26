"""HTTP transport for SPARQL and resource downloads with retry policy."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from types import TracebackType
from typing import Any

import httpx

from cellar_wrapper.constants import (
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_POOL_TIMEOUT,
    DEFAULT_READ_TIMEOUT,
    DEFAULT_RETRIES,
    DEFAULT_SPARQL_ENDPOINT,
    DEFAULT_WRITE_TIMEOUT,
    MAX_BACKOFF_SECONDS,
    RETRY_STATUS_CODES,
    SPARQL_POST_FALLBACK_STATUS_CODES,
)
from cellar_wrapper.errors import (
    CellarHTTPError,
    CellarParseError,
    CellarRateLimitError,
    CellarSPARQLError,
    CellarTimeoutError,
    CellarValidationError,
)


@dataclass(frozen=True)
class TimeoutConfig:
    """Connection timeout parameters."""

    connect: float = DEFAULT_CONNECT_TIMEOUT
    read: float = DEFAULT_READ_TIMEOUT
    write: float = DEFAULT_WRITE_TIMEOUT
    pool: float = DEFAULT_POOL_TIMEOUT


class HttpTransport:
    """Encapsulates all HTTP communication with retries."""

    def __init__(
        self,
        *,
        sparql_endpoint: str = DEFAULT_SPARQL_ENDPOINT,
        retries: int = DEFAULT_RETRIES,
        user_agent: str = "cellar-wrapper/0.1.0",
        timeout: TimeoutConfig | None = None,
    ) -> None:
        if retries < 1:
            raise CellarValidationError("retries must be >= 1")
        self._sparql_endpoint = sparql_endpoint
        self._retries = retries
        timeout_cfg = timeout or TimeoutConfig()
        self._client = httpx.Client(
            timeout=httpx.Timeout(
                connect=timeout_cfg.connect,
                read=timeout_cfg.read,
                write=timeout_cfg.write,
                pool=timeout_cfg.pool,
            ),
            follow_redirects=True,
            headers={"User-Agent": user_agent},
        )

    @property
    def sparql_endpoint(self) -> str:
        """Return current SPARQL endpoint URL."""
        return self._sparql_endpoint

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> HttpTransport:
        """Context-manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Context-manager exit."""
        self.close()

    @staticmethod
    def _media_type(value: str) -> str:
        return value.split(";", 1)[0].strip().lower()

    @classmethod
    def _is_content_type_compatible(cls, accept: str, content_type: str) -> bool:
        expected = cls._media_type(accept)
        actual = cls._media_type(content_type)
        if actual == expected:
            return True
        if actual == "application/octet-stream":
            return True
        if expected in {"application/xml", "application/rdf+xml"} and actual in {
            "application/xml",
            "application/rdf+xml",
            "text/xml",
        }:
            return True
        return False

    @staticmethod
    def _parse_retry_after_seconds(value: str | None) -> int | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            return None
        if stripped.isdigit():
            return int(stripped)

        try:
            retry_at = parsedate_to_datetime(stripped)
        except (TypeError, ValueError):
            return None
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=UTC)
        delta = retry_at - datetime.now(UTC)
        return max(0, int(delta.total_seconds()))

    def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, str] | None = None,
        data: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        last_response: httpx.Response | None = None
        for attempt in range(1, self._retries + 1):
            try:
                response = self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    headers=headers,
                )
            except httpx.TimeoutException as exc:
                if attempt == self._retries:
                    raise CellarTimeoutError(
                        f"HTTP request timed out: {exc}",
                        status_code=0,
                        url=url,
                        details={"timeout_type": type(exc).__name__},
                    ) from exc
                self._sleep_backoff(attempt)
                continue
            except httpx.HTTPError as exc:
                if attempt == self._retries:
                    raise CellarHTTPError(
                        f"HTTP request failed: {exc}",
                        status_code=0,
                        url=url,
                    ) from exc
                self._sleep_backoff(attempt)
                continue

            last_response = response
            if response.status_code in RETRY_STATUS_CODES and attempt < self._retries:
                self._sleep_backoff(attempt)
                continue

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise CellarRateLimitError(
                    "Rate limited by CELLAR endpoint",
                    status_code=429,
                    url=str(response.request.url),
                    retry_after=retry_after,
                    retry_after_seconds=self._parse_retry_after_seconds(retry_after),
                    body_excerpt=response.text[:300],
                )

            if response.status_code >= 400:
                raise CellarHTTPError(
                    f"HTTP error {response.status_code}",
                    status_code=response.status_code,
                    url=str(response.request.url),
                    body_excerpt=response.text[:300],
                )

            return response

        if last_response is None:
            raise CellarHTTPError(
                "Retry loop exhausted without receiving a response",
                status_code=0,
                url=url,
                details={"attempts": self._retries},
            )
        return last_response

    @staticmethod
    def _sleep_backoff(attempt: int) -> None:
        base = min(2 ** (attempt - 1), MAX_BACKOFF_SECONDS)
        jitter = random.uniform(0.0, 0.25)
        time.sleep(base + jitter)

    def query_sparql(self, query: str) -> dict[str, Any]:
        """Execute SPARQL query and return JSON payload."""
        accept = "application/sparql-results+json"
        request_payload = {"query": query, "format": accept}
        headers = {"Accept": accept, "Content-Type": "application/x-www-form-urlencoded"}

        try:
            response = self._request_with_retry(
                "POST",
                self._sparql_endpoint,
                data=request_payload,
                headers=headers,
            )
        except CellarHTTPError as exc:
            if exc.status_code not in SPARQL_POST_FALLBACK_STATUS_CODES:
                raise
            response = self._request_with_retry(
                "GET",
                self._sparql_endpoint,
                params=request_payload,
                headers={"Accept": accept},
            )
        try:
            payload = response.json()
        except ValueError as exc:  # pragma: no cover - defensive guard
            raise CellarSPARQLError(
                "SPARQL endpoint returned non-JSON payload",
                query=query,
                response_excerpt=response.text[:300],
            ) from exc

        if not isinstance(payload, dict):
            raise CellarSPARQLError(
                "SPARQL endpoint JSON payload is not an object",
                query=query,
                response_excerpt=str(payload)[:300],
            )
        return payload

    def download(self, url: str, *, accept: str, language: str | None = None) -> tuple[bytes, str, str]:
        """Download binary/text payload from resource endpoint."""
        headers = {"Accept": accept}
        if language is not None:
            headers["Accept-Language"] = language

        response = self._request_with_retry("GET", url, headers=headers)
        content_type = response.headers.get("Content-Type", "application/octet-stream")
        if not self._is_content_type_compatible(accept, content_type):
            raise CellarParseError(
                f"Unexpected content type from download endpoint: expected={self._media_type(accept)} got={content_type}"
            )
        return response.content, content_type, str(response.request.url)
