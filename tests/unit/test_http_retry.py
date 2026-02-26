from __future__ import annotations

import httpx
import pytest

from cellar_wrapper.errors import CellarHTTPError
from cellar_wrapper.http import HttpTransport


def _response(status_code: int, *, json_body: dict[str, object] | None = None) -> httpx.Response:
    request = httpx.Request("GET", "https://example.test/sparql")
    if json_body is not None:
        return httpx.Response(status_code, request=request, json=json_body)
    return httpx.Response(status_code, request=request, text="error")


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
