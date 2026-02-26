from __future__ import annotations

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
from cellar_wrapper.http import HttpTransport


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


def test_transport_retries_below_one_raises_validation_error() -> None:
    with pytest.raises(CellarValidationError, match="retries must be >= 1"):
        HttpTransport(retries=0)


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


def test_backoff_is_capped(monkeypatch: pytest.MonkeyPatch) -> None:
    capture: dict[str, float] = {}

    monkeypatch.setattr("cellar_wrapper.http.time.sleep", lambda value: capture.setdefault("sleep", value))
    monkeypatch.setattr("cellar_wrapper.http.random.uniform", lambda *_: 0.25)

    HttpTransport._sleep_backoff(10)

    assert capture["sleep"] <= 8.25


def test_transport_context_manager_closes_client(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(sparql_endpoint="https://example.test/sparql", retries=1)
    closed = {"value": False}

    def fake_close() -> None:
        closed["value"] = True

    monkeypatch.setattr(transport._client, "close", fake_close)

    with transport as active:
        assert active is transport
    assert closed["value"] is True


def test_download_rejects_incompatible_content_type(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(retries=1)

    def fake_request(*args: object, **kwargs: object) -> httpx.Response:
        request = httpx.Request("GET", "https://example.test/file")
        return httpx.Response(200, request=request, headers={"Content-Type": "text/html"}, text="<html></html>")

    monkeypatch.setattr(transport._client, "request", fake_request)

    with pytest.raises(CellarParseError, match="Unexpected content type"):
        transport.download("https://example.test/file", accept="application/pdf")
    transport.close()


def test_download_allows_octet_stream_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HttpTransport(retries=1)

    def fake_request(*args: object, **kwargs: object) -> httpx.Response:
        request = httpx.Request("GET", "https://example.test/file")
        return httpx.Response(200, request=request, headers={"Content-Type": "application/octet-stream"}, content=b"pdf")

    monkeypatch.setattr(transport._client, "request", fake_request)

    content, content_type, _ = transport.download("https://example.test/file", accept="application/pdf")
    assert content == b"pdf"
    assert content_type == "application/octet-stream"
    transport.close()
