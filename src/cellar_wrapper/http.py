"""HTTP transport for SPARQL and resource downloads with retry policy."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from types import TracebackType
from typing import Any
from urllib.parse import urlparse

import httpx

from cellar_wrapper.constants import (
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_MAX_DOWNLOAD_BYTES,
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

MAX_SPARQL_GET_FALLBACK_URL_LENGTH = 8_000


def validate_http_url(url: str, *, field: str) -> str:
    """Validate http/https URL string and return normalized value."""
    candidate = url.strip()
    if not candidate:
        raise CellarValidationError(f"{field} cannot be empty")
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise CellarValidationError(f"Invalid URL for {field}: {url!r}")
    return candidate


@dataclass(frozen=True)
class TimeoutConfig:
    """Connection timeout parameters."""

    connect: float = DEFAULT_CONNECT_TIMEOUT
    read: float = DEFAULT_READ_TIMEOUT
    write: float = DEFAULT_WRITE_TIMEOUT
    pool: float = DEFAULT_POOL_TIMEOUT

    def __post_init__(self) -> None:
        for field_name, field_value in (
            ("connect", self.connect),
            ("read", self.read),
            ("write", self.write),
            ("pool", self.pool),
        ):
            if field_value <= 0:
                raise CellarValidationError(f"timeout.{field_name} must be > 0")


class HttpTransport:
    """Encapsulates all HTTP communication with retries."""

    def __init__(
        self,
        *,
        sparql_endpoint: str = DEFAULT_SPARQL_ENDPOINT,
        retries: int = DEFAULT_RETRIES,
        max_download_bytes: int = DEFAULT_MAX_DOWNLOAD_BYTES,
        user_agent: str = "cellar-wrapper/0.1.0",
        timeout: TimeoutConfig | None = None,
    ) -> None:
        if retries < 1:
            raise CellarValidationError("retries must be >= 1")
        if max_download_bytes < 1:
            raise CellarValidationError("max_download_bytes must be >= 1")
        self._sparql_endpoint = validate_http_url(sparql_endpoint, field="sparql_endpoint")
        self._max_download_bytes = max_download_bytes
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

    @staticmethod
    def _clamp_retry_after_seconds(value: int | None) -> int | None:
        if value is None:
            return None
        return min(value, int(MAX_BACKOFF_SECONDS))

    @staticmethod
    def _sleep_retry_after_or_backoff(retry_after_seconds: int | None, attempt: int) -> None:
        if retry_after_seconds is not None:
            time.sleep(retry_after_seconds)
            return
        HttpTransport._sleep_backoff(attempt)

    @staticmethod
    def _raise_http_error_from_response(response: httpx.Response) -> None:
        raise CellarHTTPError(
            f"HTTP error {response.status_code}",
            status_code=response.status_code,
            url=str(response.request.url),
            body_excerpt=response.text[:300],
        )

    @staticmethod
    def _raise_rate_limit_error(
        response: httpx.Response,
        *,
        retry_after: str | None,
        retry_after_seconds: int | None,
    ) -> None:
        raise CellarRateLimitError(
            "Rate limited by CELLAR endpoint",
            status_code=429,
            url=str(response.request.url),
            retry_after=retry_after,
            retry_after_seconds=retry_after_seconds,
            body_excerpt=response.text[:300],
        )

    def _handle_rate_limit_response(self, response: httpx.Response, *, attempt: int) -> bool:
        if response.status_code != 429:
            return False

        retry_after = response.headers.get("Retry-After")
        retry_after_seconds = self._clamp_retry_after_seconds(
            self._parse_retry_after_seconds(retry_after)
        )
        if attempt < self._retries:
            self._sleep_retry_after_or_backoff(retry_after_seconds, attempt)
            return True

        self._raise_rate_limit_error(
            response,
            retry_after=retry_after,
            retry_after_seconds=retry_after_seconds,
        )
        return False

    def _retry_or_raise_timeout(self, exc: httpx.TimeoutException, *, url: str, attempt: int) -> None:
        if attempt == self._retries:
            raise CellarTimeoutError(
                f"HTTP request timed out: {exc}",
                status_code=0,
                url=url,
                details={"timeout_type": type(exc).__name__},
            ) from exc
        self._sleep_backoff(attempt)

    def _retry_or_raise_http_error(self, exc: httpx.HTTPError, *, url: str, attempt: int) -> None:
        if attempt == self._retries:
            raise CellarHTTPError(
                f"HTTP request failed: {exc}",
                status_code=0,
                url=url,
            ) from exc
        self._sleep_backoff(attempt)

    def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, str] | None = None,
        data: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
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
                self._retry_or_raise_timeout(exc, url=url, attempt=attempt)
                continue
            except httpx.HTTPError as exc:
                self._retry_or_raise_http_error(exc, url=url, attempt=attempt)
                continue

            if self._handle_rate_limit_response(response, attempt=attempt):
                continue

            if response.status_code in RETRY_STATUS_CODES and attempt < self._retries:
                self._sleep_backoff(attempt)
                continue

            if response.status_code >= 400:
                self._raise_http_error_from_response(response)

            return response

        raise CellarHTTPError(
            "Retry loop exhausted without receiving a response",
            status_code=0,
            url=url,
            details={"attempts": self._retries},
        )

    @staticmethod
    def _sleep_backoff(attempt: int) -> None:
        base = min(2 ** (attempt - 1), MAX_BACKOFF_SECONDS)
        delay = random.uniform(0.0, base)
        time.sleep(delay)

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
            fallback_request = self._client.build_request(
                "GET",
                self._sparql_endpoint,
                params=request_payload,
                headers={"Accept": accept},
            )
            fallback_url_length = len(str(fallback_request.url))
            if fallback_url_length > MAX_SPARQL_GET_FALLBACK_URL_LENGTH:
                raise CellarSPARQLError(
                    "SPARQL GET fallback URL exceeds safe length",
                    query=query,
                    details={
                        "max_url_length": MAX_SPARQL_GET_FALLBACK_URL_LENGTH,
                        "actual_url_length": fallback_url_length,
                    },
                ) from exc
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

    def _validate_download_content_type(self, *, accept: str, content_type: str) -> None:
        if self._is_content_type_compatible(accept, content_type):
            return
        raise CellarParseError(
            f"Unexpected content type from download endpoint: expected={self._media_type(accept)} got={content_type}",
            details={
                "expected_content_type": self._media_type(accept),
                "content_type": content_type,
            },
        )

    def _raise_download_size_error(self, response: httpx.Response, *, received_bytes: int) -> None:
        raise CellarHTTPError(
            "Download exceeds max_download_bytes",
            status_code=response.status_code,
            url=str(response.request.url),
            details={
                "max_download_bytes": self._max_download_bytes,
                "received_bytes": received_bytes,
            },
        )

    def _validate_content_length_header(self, response: httpx.Response) -> None:
        raw_content_length = response.headers.get("Content-Length")
        if raw_content_length is None or not raw_content_length.isdigit():
            return
        content_length = int(raw_content_length)
        if content_length > self._max_download_bytes:
            self._raise_download_size_error(response, received_bytes=content_length)

    def _read_download_content(self, response: httpx.Response) -> bytes:
        content = bytearray()
        for chunk in response.iter_bytes():
            content.extend(chunk)
            if len(content) > self._max_download_bytes:
                self._raise_download_size_error(response, received_bytes=len(content))
        return bytes(content)

    def _handle_download_response(
        self,
        response: httpx.Response,
        *,
        accept: str,
        attempt: int,
    ) -> tuple[bytes, str, str] | None:
        if self._handle_rate_limit_response(response, attempt=attempt):
            return None
        if response.status_code in RETRY_STATUS_CODES and attempt < self._retries:
            self._sleep_backoff(attempt)
            return None
        if response.status_code >= 400:
            self._raise_http_error_from_response(response)

        content_type = response.headers.get("Content-Type", "application/octet-stream")
        self._validate_download_content_type(accept=accept, content_type=content_type)
        self._validate_content_length_header(response)
        content = self._read_download_content(response)
        return content, content_type, str(response.request.url)

    def download(self, url: str, *, accept: str, language: str | None = None) -> tuple[bytes, str, str]:
        """Download binary/text payload from resource endpoint."""
        download_url = validate_http_url(url, field="download_url")
        headers = {"Accept": accept}
        if language is not None:
            headers["Accept-Language"] = language

        for attempt in range(1, self._retries + 1):
            try:
                with self._client.stream("GET", download_url, headers=headers) as response:
                    payload = self._handle_download_response(
                        response,
                        accept=accept,
                        attempt=attempt,
                    )
                    if payload is not None:
                        return payload

            except httpx.TimeoutException as exc:
                self._retry_or_raise_timeout(exc, url=download_url, attempt=attempt)
                continue
            except httpx.HTTPError as exc:
                self._retry_or_raise_http_error(exc, url=download_url, attempt=attempt)
                continue

        raise CellarHTTPError(
            "Retry loop exhausted without receiving a response",
            status_code=0,
            url=download_url,
            details={"attempts": self._retries},
        )
