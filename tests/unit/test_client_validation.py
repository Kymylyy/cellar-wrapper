from __future__ import annotations

import pytest

from cellar_wrapper.client import CellarClient
from cellar_wrapper.constants import SUMMARY_ACCEPT
from cellar_wrapper.errors import CellarNotFoundError, CellarValidationError
from tests.helpers import FakeTransport, sparql_payload, sparql_row


def test_invalid_celex_raises_validation_error() -> None:
    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarValidationError):
        client.resolve_celex("bad celex")


def test_invalid_language_raises_validation_error() -> None:
    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarValidationError):
        client.get_text("32022R2554", lang="english")


def test_limit_above_max_raises_validation_error() -> None:
    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarValidationError):
        client.search_by_title("dora", limit=1001)


def test_invalid_since_in_monitoring_raises_validation_error() -> None:
    transport = FakeTransport()
    client = CellarClient(transport=transport)
    with pytest.raises(CellarValidationError):
        client.new_citations("32022R2554", since="not-a-date")


def test_retries_below_one_raises_validation_error() -> None:
    with pytest.raises(CellarValidationError, match="retries must be >= 1"):
        CellarClient(retries=0)


def test_resolve_celex_exact_then_contains_fallback() -> None:
    def query_handler(query: str) -> dict[str, object]:
        if "FILTER(UCASE(STR(?celex))" in query:
            return sparql_payload([])
        if "FILTER(CONTAINS(UCASE(STR(?celex))" in query:
            return sparql_payload(
                [
                    sparql_row(
                        work="http://publications.europa.eu/resource/cellar/abc",
                        celex="32022R2554",
                    )
                ]
            )
        return sparql_payload([])

    transport = FakeTransport(query_handler=query_handler)
    client = CellarClient(transport=transport)
    resolved = client.resolve_celex("32022R2554")

    assert resolved.uri == "http://publications.europa.eu/resource/cellar/abc"
    assert len(transport.queries) == 2
    assert "CONTAINS" in transport.queries[1]


def test_resolve_celex_fallback_requires_exact_match() -> None:
    def query_handler(query: str) -> dict[str, object]:
        if "FILTER(UCASE(STR(?celex))" in query:
            return sparql_payload([])
        if "FILTER(CONTAINS(UCASE(STR(?celex))" in query:
            return sparql_payload(
                [
                    sparql_row(
                        work="http://publications.europa.eu/resource/cellar/other",
                        celex="12022R2554",
                    )
                ]
            )
        return sparql_payload([])

    transport = FakeTransport(query_handler=query_handler)
    client = CellarClient(transport=transport)
    with pytest.raises(CellarNotFoundError, match="Fallback did not return exact CELEX"):
        client.resolve_celex("32022R2554")


def test_search_by_title_empty_keyword_raises_validation_error() -> None:
    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarValidationError, match="keyword cannot be empty"):
        client.search_by_title("   ")


def test_search_by_eurovoc_empty_tags_raises_validation_error() -> None:
    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarValidationError, match="tags cannot be empty"):
        client.search_by_eurovoc([])


def test_search_by_subject_matter_empty_codes_raises_validation_error() -> None:
    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarValidationError, match="codes cannot be empty"):
        client.search_by_subject_matter([" ", "\t"])


def test_summary_download_uses_xhtml5_accept() -> None:
    def query_handler(query: str) -> dict[str, object]:
        if "summary_summarizes_work" in query:
            return sparql_payload(
                [
                    sparql_row(
                        summary="http://publications.europa.eu/resource/legissum/2404020302_1"
                    )
                ]
            )
        return sparql_payload(
            [
                sparql_row(
                    work="http://publications.europa.eu/resource/cellar/act",
                    celex="32015L2366",
                )
            ]
        )

    def download_handler(url: str, accept: str, language: str | None) -> tuple[bytes, str, str]:
        assert url.startswith("http://publications.europa.eu/resource/legissum")
        assert accept == SUMMARY_ACCEPT
        assert language == "eng"
        return (b"summary", "application/xhtml+xml", url)

    transport = FakeTransport(query_handler=query_handler, download_handler=download_handler)
    client = CellarClient(transport=transport)
    payload = client.get_summary("32015L2366")

    assert payload.content_base64
    assert transport.downloads[0][1] == SUMMARY_ACCEPT


def test_client_context_manager_closes_transport() -> None:
    class ClosableTransport(FakeTransport):
        def __init__(self) -> None:
            super().__init__()
            self.closed = False

        def close(self) -> None:
            self.closed = True

    transport = ClosableTransport()
    with CellarClient(transport=transport):
        pass
    assert transport.closed is True
