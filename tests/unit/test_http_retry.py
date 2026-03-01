from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from email.utils import format_datetime

import httpx
import pytest

from cellar_wrapper.errors import (
    CellarHTTPError,
    CellarParseError,
    CellarRateLimitError,
    CellarSPARQLError,
    CellarTimeoutError,
    CellarValidationError,
)
from cellar_wrapper.http import HttpTransport, TimeoutConfig


def _response(
    status_code: int,
    *,
    json_body: dict[str, object] | None = None,
    method: str = "POST",
) -> httpx.Response:
    request = httpx.Request(method, "https://example.test/sparql")
    if json_body is not None:
        return httpx.Response(status_code, request=request, json=json_body)
    return httpx.Response(status_code, request=request, text="error")


@contextmanager
def _stream_response(response: httpx.Response) -> Generator[httpx.Response, None, None]:
    yield response


def test_transport_retries_below_one_raises_validation_error() -> None:
    with pytest.raises(CellarValidationError, match="retries must be >= 1"):
        HttpTransport(retries=0)


def test_transport_validates_sparql_endpoint_url() -> None:
    with pytest.raises(CellarValidationError, match="sparql_endpoint"):
        HttpTransport(sparql_endpoint="ftp://example.test/sparql")


def test_timeout_config_requires_positive_values() -> None:
    with pytest.raises(CellarValidationError, match="timeout.connect must be > 0"):
        TimeoutConfig(connect=0)


def test_retry_on_503_then_success(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(sparql_endpoint="https://example.test/sparql", retries=2)
    calls = {"count": 0}
    responses = iter(
        [
            _response(503),
            _response(200, json_body={"results": {"bindings": []}}),
        ]
    )

    def fake_request(*args: object, **kwargs: object) -> httpx.Response:
        calls["count"] += 1
        return next(responses)

    monkeypatch.setattr(transport._client, "request", fake_request)
    monkeypatch.setattr("cellar_wrapper.http.time.sleep", lambda *_: None)
    monkeypatch.setattr("cellar_wrapper.http.random.uniform", lambda *_: 0.0)

    payload = transport.query_sparql("SELECT * WHERE { ?s ?p ?o }")
    assert payload == {"results": {"bindings": []}}
    assert calls["count"] == 2
    transport.close()


def test_intermediate_429_uses_retry_after(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(sparql_endpoint="https://example.test/sparql", retries=2)
    responses = iter(
        [
            httpx.Response(
                429,
                request=httpx.Request("POST", "https://example.test/sparql"),
                headers={"Retry-After": "5"},
                text="slow down",
            ),
            _response(200, json_body={"results": {"bindings": []}}),
        ]
    )
    sleeps: list[float] = []

    def fake_request(*args: object, **kwargs: object) -> httpx.Response:
        return next(responses)

    monkeypatch.setattr(transport._client, "request", fake_request)
    monkeypatch.setattr("cellar_wrapper.http.time.sleep", lambda value: sleeps.append(value))
    monkeypatch.setattr("cellar_wrapper.http.random.uniform", lambda *_: 0.0)

    payload = transport.query_sparql("SELECT * WHERE { ?s ?p ?o }")
    assert payload == {"results": {"bindings": []}}
    assert sleeps == [5]
    transport.close()


def test_query_sparql_uses_post_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(sparql_endpoint="https://example.test/sparql", retries=1)
    methods: list[str] = []

    def fake_request(*args: object, **kwargs: object) -> httpx.Response:
        method = kwargs["method"]
        methods.append(method)
        return _response(200, json_body={"results": {"bindings": []}}, method=method)

    monkeypatch.setattr(transport._client, "request", fake_request)

    payload = transport.query_sparql("SELECT * WHERE { ?s ?p ?o }")
    assert payload == {"results": {"bindings": []}}
    assert methods == ["POST"]
    transport.close()


def test_query_sparql_falls_back_to_get_when_post_not_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(sparql_endpoint="https://example.test/sparql", retries=1)
    methods: list[str] = []

    def fake_request(*args: object, **kwargs: object) -> httpx.Response:
        method = kwargs["method"]
        methods.append(method)
        if method == "POST":
            return _response(405, method=method)
        return _response(200, json_body={"results": {"bindings": []}}, method=method)

    monkeypatch.setattr(transport._client, "request", fake_request)

    payload = transport.query_sparql("SELECT * WHERE { ?s ?p ?o }")
    assert payload == {"results": {"bindings": []}}
    assert methods == ["POST", "GET"]
    transport.close()


def test_query_sparql_blocks_get_fallback_when_url_too_long(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(sparql_endpoint="https://example.test/sparql", retries=1)
    methods: list[str] = []

    def fake_request(*args: object, **kwargs: object) -> httpx.Response:
        method = kwargs["method"]
        methods.append(method)
        if method == "POST":
            return _response(405, method=method)
        raise AssertionError("GET fallback should be blocked by URL length guard")

    monkeypatch.setattr(transport._client, "request", fake_request)
    monkeypatch.setattr("cellar_wrapper.http.MAX_SPARQL_GET_FALLBACK_URL_LENGTH", 120)

    long_query = "SELECT * WHERE { ?s ?p ?o } " + (" OPTIONAL { ?s ?p ?o }" * 200)
    with pytest.raises(CellarSPARQLError, match="GET fallback URL exceeds safe length") as exc_info:
        transport.query_sparql(long_query)

    assert exc_info.value.details["actual_url_length"] > exc_info.value.details["max_url_length"]
    assert methods == ["POST"]
    transport.close()


def test_no_retry_on_400(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(sparql_endpoint="https://example.test/sparql", retries=3)
    calls = {"count": 0}

    def fake_request(*args: object, **kwargs: object) -> httpx.Response:
        calls["count"] += 1
        return _response(400)

    monkeypatch.setattr(transport._client, "request", fake_request)

    with pytest.raises(CellarHTTPError):
        transport.query_sparql("SELECT * WHERE { ?s ?p ?o }")

    assert calls["count"] == 1
    transport.close()


def test_timeout_raises_cellar_timeout_error(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(sparql_endpoint="https://example.test/sparql", retries=1)

    def fake_request(*args: object, **kwargs: object) -> httpx.Response:
        request = httpx.Request("GET", "https://example.test/sparql")
        raise httpx.ReadTimeout("timed out", request=request)

    monkeypatch.setattr(transport._client, "request", fake_request)

    with pytest.raises(CellarTimeoutError) as exc_info:
        transport.query_sparql("SELECT * WHERE { ?s ?p ?o }")

    assert exc_info.value.details["timeout_type"] == "ReadTimeout"
    transport.close()


def test_rate_limit_parses_retry_after_seconds(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(sparql_endpoint="https://example.test/sparql", retries=1)

    def fake_request(*args: object, **kwargs: object) -> httpx.Response:
        request = httpx.Request("GET", "https://example.test/sparql")
        return httpx.Response(429, request=request, headers={"Retry-After": "120"}, text="slow down")

    monkeypatch.setattr(transport._client, "request", fake_request)

    with pytest.raises(CellarRateLimitError) as exc_info:
        transport.query_sparql("SELECT * WHERE { ?s ?p ?o }")

    assert exc_info.value.retry_after == "120"
    assert exc_info.value.retry_after_seconds == 120
    transport.close()


def test_non_json_sparql_response_has_query_context(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(sparql_endpoint="https://example.test/sparql", retries=1)

    def fake_request(*args: object, **kwargs: object) -> httpx.Response:
        request = httpx.Request("GET", "https://example.test/sparql")
        return httpx.Response(200, request=request, text="not-json")

    monkeypatch.setattr(transport._client, "request", fake_request)

    query = "SELECT * WHERE { ?s ?p ?o }"
    with pytest.raises(CellarSPARQLError) as exc_info:
        transport.query_sparql(query)

    assert exc_info.value.query == query
    assert "not-json" in (exc_info.value.response_excerpt or "")
    transport.close()


def test_sparql_rejects_non_object_json_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(sparql_endpoint="https://example.test/sparql", retries=1)

    def fake_request(*args: object, **kwargs: object) -> httpx.Response:
        request = httpx.Request("POST", "https://example.test/sparql")
        return httpx.Response(200, request=request, json=["not", "an", "object"])

    monkeypatch.setattr(transport._client, "request", fake_request)

    with pytest.raises(CellarSPARQLError, match="payload is not an object"):
        transport.query_sparql("SELECT * WHERE { ?s ?p ?o }")
    transport.close()


def test_backoff_full_jitter_uses_cap(monkeypatch: pytest.MonkeyPatch) -> None:
    capture: dict[str, float] = {}

    monkeypatch.setattr("cellar_wrapper.http.time.sleep", lambda value: capture.setdefault("sleep", value))
    monkeypatch.setattr("cellar_wrapper.http.random.uniform", lambda _low, high: high)

    HttpTransport._sleep_backoff(10)

    assert capture["sleep"] <= 8.0


def test_transport_context_manager_closes_client(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(sparql_endpoint="https://example.test/sparql", retries=1)
    closed = {"value": False}

    def fake_close() -> None:
        closed["value"] = True

    monkeypatch.setattr(transport._client, "close", fake_close)

    with transport as active:
        assert active is transport
    assert closed["value"] is True


def test_download_rejects_invalid_url() -> None:
    transport = HttpTransport(retries=1)

    with pytest.raises(CellarValidationError, match="download_url"):
        transport.download("ftp://example.test/file", accept="application/pdf")
    transport.close()


def test_download_retries_on_429_with_retry_after_seconds(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(retries=2)
    responses = iter(
        [
            httpx.Response(
                429,
                request=httpx.Request("GET", "https://example.test/file"),
                headers={"Retry-After": "5"},
                text="slow down",
            ),
            httpx.Response(
                200,
                request=httpx.Request("GET", "https://example.test/file"),
                headers={"Content-Type": "application/pdf"},
                content=b"ok",
            ),
        ]
    )
    sleeps: list[float] = []

    def fake_stream(*args: object, **kwargs: object) -> object:
        return _stream_response(next(responses))

    monkeypatch.setattr(transport._client, "stream", fake_stream)
    monkeypatch.setattr("cellar_wrapper.http.time.sleep", lambda value: sleeps.append(float(value)))

    content, content_type, _ = transport.download("https://example.test/file", accept="application/pdf")
    assert content == b"ok"
    assert content_type == "application/pdf"
    assert sleeps == [5.0]
    transport.close()


def test_download_retries_on_429_with_retry_after_http_date(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(retries=2)
    retry_at = datetime.now(UTC) + timedelta(hours=1)
    responses = iter(
        [
            httpx.Response(
                429,
                request=httpx.Request("GET", "https://example.test/file"),
                headers={"Retry-After": format_datetime(retry_at, usegmt=True)},
                text="slow down",
            ),
            httpx.Response(
                200,
                request=httpx.Request("GET", "https://example.test/file"),
                headers={"Content-Type": "application/pdf"},
                content=b"ok",
            ),
        ]
    )
    sleeps: list[float] = []

    def fake_stream(*args: object, **kwargs: object) -> object:
        return _stream_response(next(responses))

    monkeypatch.setattr(transport._client, "stream", fake_stream)
    monkeypatch.setattr("cellar_wrapper.http.time.sleep", lambda value: sleeps.append(float(value)))

    content, content_type, _ = transport.download("https://example.test/file", accept="application/pdf")
    assert content == b"ok"
    assert content_type == "application/pdf"
    assert len(sleeps) == 1
    assert sleeps[0] >= 3500.0
    transport.close()


def test_download_rejects_incompatible_content_type(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(retries=1)

    def fake_stream(*args: object, **kwargs: object) -> object:
        request = httpx.Request("GET", "https://example.test/file")
        response = httpx.Response(
            200,
            request=request,
            headers={"Content-Type": "text/html"},
            text="<html></html>",
        )
        return _stream_response(response)

    monkeypatch.setattr(transport._client, "stream", fake_stream)

    with pytest.raises(CellarParseError, match="Unexpected content type"):
        transport.download("https://example.test/file", accept="application/pdf")
    transport.close()


def test_download_timeout_after_retries_raises_structured_error(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(retries=2)

    def fake_stream(*args: object, **kwargs: object) -> object:
        request = httpx.Request("GET", "https://example.test/file")
        raise httpx.ReadTimeout("timed out", request=request)

    monkeypatch.setattr(transport._client, "stream", fake_stream)
    monkeypatch.setattr("cellar_wrapper.http.time.sleep", lambda *_: None)
    monkeypatch.setattr("cellar_wrapper.http.random.uniform", lambda *_: 0.0)

    with pytest.raises(CellarTimeoutError) as exc_info:
        transport.download("https://example.test/file", accept="application/pdf")

    assert exc_info.value.details["timeout_type"] == "ReadTimeout"
    transport.close()


def test_download_http_error_after_retries_raises_structured_error(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(retries=2)

    def fake_stream(*args: object, **kwargs: object) -> object:
        request = httpx.Request("GET", "https://example.test/file")
        raise httpx.ConnectError("network down", request=request)

    monkeypatch.setattr(transport._client, "stream", fake_stream)
    monkeypatch.setattr("cellar_wrapper.http.time.sleep", lambda *_: None)
    monkeypatch.setattr("cellar_wrapper.http.random.uniform", lambda *_: 0.0)

    with pytest.raises(CellarHTTPError, match="HTTP request failed"):
        transport.download("https://example.test/file", accept="application/pdf")
    transport.close()


def test_download_allows_octet_stream_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(retries=1)

    def fake_stream(*args: object, **kwargs: object) -> object:
        request = httpx.Request("GET", "https://example.test/file")
        response = httpx.Response(
            200,
            request=request,
            headers={"Content-Type": "application/octet-stream"},
            content=b"pdf",
        )
        return _stream_response(response)

    monkeypatch.setattr(transport._client, "stream", fake_stream)

    content, content_type, _ = transport.download("https://example.test/file", accept="application/pdf")
    assert content == b"pdf"
    assert content_type == "application/octet-stream"
    transport.close()


def test_download_over_size_limit_returns_structured_error(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(retries=1, max_download_bytes=3)

    def fake_stream(*args: object, **kwargs: object) -> object:
        request = httpx.Request("GET", "https://example.test/file")
        response = httpx.Response(
            200,
            request=request,
            headers={"Content-Type": "application/pdf"},
            content=b"abcd",
        )
        return _stream_response(response)

    monkeypatch.setattr(transport._client, "stream", fake_stream)

    with pytest.raises(CellarHTTPError, match="max_download_bytes") as exc_info:
        transport.download("https://example.test/file", accept="application/pdf")

    assert exc_info.value.details["max_download_bytes"] == 3
    assert exc_info.value.details["received_bytes"] >= 4
    transport.close()
