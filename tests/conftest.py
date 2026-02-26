from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FakeTransport:
    """Simple in-memory transport for tests."""

    sparql_endpoint: str = "https://example.test/sparql"
    query_handler: Callable[[str], dict[str, Any]] | None = None
    download_handler: Callable[[str, str, str | None], tuple[bytes, str, str]] | None = None
    queries: list[str] = field(default_factory=list)
    downloads: list[tuple[str, str, str | None]] = field(default_factory=list)

    def query_sparql(self, query: str) -> dict[str, Any]:
        self.queries.append(query)
        if self.query_handler is None:
            return {"results": {"bindings": []}}
        return self.query_handler(query)

    def download(self, url: str, *, accept: str, language: str | None = None) -> tuple[bytes, str, str]:
        self.downloads.append((url, accept, language))
        if self.download_handler is None:
            return (b"", "application/octet-stream", url)
        return self.download_handler(url, accept, language)

    def close(self) -> None:
        return None


def sparql_binding(**values: str) -> dict[str, dict[str, str]]:
    return {key: {"type": "literal", "value": value} for key, value in values.items()}


def sparql_uri_binding(**values: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for key, value in values.items():
        value_type = "uri" if value.startswith("http") else "literal"
        result[key] = {"type": value_type, "value": value}
    return result
