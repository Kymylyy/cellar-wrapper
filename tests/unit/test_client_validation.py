from __future__ import annotations

from typing import Any, cast

import pytest

from cellar_wrapper.client import CellarClient
from cellar_wrapper.constants import SUMMARY_ACCEPT
from cellar_wrapper.errors import (
    CellarHTTPError,
    CellarNotFoundError,
    CellarParseError,
    CellarValidationError,
)
from tests.helpers import FakeTransport, sparql_payload, sparql_row


def test_invalid_celex_raises_validation_error() -> None:
    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarValidationError):
        client.resolve_celex("bad celex")


def test_invalid_language_raises_validation_error() -> None:
    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarValidationError):
        client.get_text("32022R2554", lang="english")


def test_invalid_direction_raises_validation_error() -> None:
    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarValidationError, match="Invalid direction"):
        client.get_amendments("32022R2554", direction=cast(Any, "sideways"))


def test_limit_above_max_raises_validation_error() -> None:
    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarValidationError):
        client.search_by_title("dora", limit=1001)


def test_invalid_since_in_monitoring_raises_validation_error() -> None:
    transport = FakeTransport()
    client = CellarClient(transport=transport)
    with pytest.raises(CellarValidationError):
        client.new_citations("32022R2554", since="not-a-date")


def test_invalid_country_code_raises_validation_error() -> None:
    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarValidationError, match="Invalid country code"):
        client.get_national_decisions("32022R2554", country="DE")


def test_retries_below_one_raises_validation_error() -> None:
    with pytest.raises(CellarValidationError, match="retries must be >= 1"):
        CellarClient(retries=0)


def test_resolve_celex_not_found_has_structured_details() -> None:
    transport = FakeTransport(query_handler=lambda _query: sparql_payload([]))
    client = CellarClient(transport=transport)

    with pytest.raises(CellarNotFoundError, match="CELEX not found in CELLAR") as exc_info:
        client.resolve_celex("32022R2554")

    assert exc_info.value.details["entity"] == "celex"
    assert exc_info.value.details["celex"] == "32022R2554"
    assert exc_info.value.details["phase"] == "resolve_exact_then_contains"


def test_invalid_base_urls_raise_validation_error() -> None:
    with pytest.raises(CellarValidationError, match="base_url_sparql"):
        CellarClient(base_url_sparql="ftp://example.test/sparql", transport=FakeTransport())
    with pytest.raises(CellarValidationError, match="base_url_resource"):
        CellarClient(base_url_resource="ftp://example.test/resource", transport=FakeTransport())


def test_max_download_bytes_must_be_positive() -> None:
    with pytest.raises(CellarValidationError, match="max_download_bytes must be >= 1"):
        CellarClient(max_download_bytes=0, transport=FakeTransport())


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


def test_search_by_title_empty_resource_types_raises_validation_error() -> None:
    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarValidationError, match="resource_types cannot be empty"):
        client.search_by_title("dora", resource_types=[])


def test_search_by_title_invalid_resource_type_token_raises_validation_error() -> None:
    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarValidationError, match="Invalid resource_type"):
        client.search_by_title("dora", resource_types=["PROP-REG"])


def test_search_by_eurovoc_empty_tags_raises_validation_error() -> None:
    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarValidationError, match="tags cannot be empty"):
        client.search_by_eurovoc([])


def test_find_eurovoc_concept_fails_fast_when_local_index_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise_parse_error() -> object:
        raise CellarParseError(
            "Failed to load local EuroVoc index",
            details={"source": "local_eurovoc_index"},
        )

    monkeypatch.setattr("cellar_wrapper.client_mixins.base.load_default_eurovoc_index", _raise_parse_error)

    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarParseError, match="Failed to load local EuroVoc index"):
        client.find_eurovoc_concept("payment")


def test_search_by_subject_matter_empty_codes_raises_validation_error() -> None:
    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarValidationError, match="codes cannot be empty"):
        client.search_by_subject_matter([" ", "\t"])


def test_search_by_subject_matter_fails_fast_when_local_index_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise_parse_error() -> object:
        raise CellarParseError(
            "Failed to load local subject-matter index",
            details={"source": "local_subject_matter_index"},
        )

    monkeypatch.setattr(
        "cellar_wrapper.client_mixins.base.load_default_subject_matter_index",
        _raise_parse_error,
    )

    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarParseError, match="Failed to load local subject-matter index"):
        client.search_by_subject_matter(["data protection"])


def test_search_by_subject_matter_returns_empty_without_live_query_when_no_match(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _EmptySubjectMatterIndex:
        @staticmethod
        def resolve_concept_uris(_codes: list[str]) -> list[str]:
            return []

    monkeypatch.setattr(
        "cellar_wrapper.client_mixins.base.load_default_subject_matter_index",
        lambda: _EmptySubjectMatterIndex(),
    )

    transport = FakeTransport()
    client = CellarClient(transport=transport)
    result = client.search_by_subject_matter(["no-such-subject"])

    assert result.returned_count == 0
    assert result.items == []
    assert transport.queries == []


def test_get_text_missing_celex_raises_not_found() -> None:
    client = CellarClient(transport=FakeTransport())
    with pytest.raises(CellarNotFoundError, match="CELEX not found"):
        client.get_text("32022R2554")


def test_get_text_404_download_raises_not_found() -> None:
    def query_handler(query: str) -> dict[str, object]:
        if "FILTER(UCASE(STR(?celex))" in query:
            return sparql_payload(
                [
                    sparql_row(
                        work="http://publications.europa.eu/resource/cellar/act",
                        celex="32022R2554",
                    )
                ]
            )
        return sparql_payload([])

    def download_handler(url: str, _accept: str, _language: str | None) -> tuple[bytes, str, str]:
        raise CellarHTTPError("HTTP error 404", status_code=404, url=url)

    client = CellarClient(
        transport=FakeTransport(query_handler=query_handler, download_handler=download_handler)
    )
    with pytest.raises(CellarNotFoundError, match="No document content found for CELEX") as exc_info:
        client.get_text("32022R2554")

    assert exc_info.value.details["entity"] == "document"
    assert exc_info.value.details["celex"] == "32022R2554"
    assert exc_info.value.details["lang"] == "eng"
    assert exc_info.value.details["format"] == "pdf"


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


def test_get_summary_404_download_raises_not_found() -> None:
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

    def download_handler(url: str, _accept: str, _language: str | None) -> tuple[bytes, str, str]:
        raise CellarHTTPError("HTTP error 404", status_code=404, url=url)

    client = CellarClient(
        transport=FakeTransport(query_handler=query_handler, download_handler=download_handler)
    )

    with pytest.raises(CellarNotFoundError, match="No legislative summary found for CELEX") as exc_info:
        client.get_summary("32015L2366")

    assert exc_info.value.details["entity"] == "summary"
    assert exc_info.value.details["celex"] == "32015L2366"
    assert exc_info.value.details["lang"] == "eng"


def test_get_summary_not_found_has_structured_details() -> None:
    def query_handler(query: str) -> dict[str, object]:
        if "summary_summarizes_work" in query:
            return sparql_payload([])
        return sparql_payload(
            [
                sparql_row(
                    work="http://publications.europa.eu/resource/cellar/act",
                    celex="32015L2366",
                )
            ]
        )

    transport = FakeTransport(query_handler=query_handler)
    client = CellarClient(transport=transport)

    with pytest.raises(CellarNotFoundError, match="No legislative summary found for CELEX") as exc_info:
        client.get_summary("32015L2366")

    assert exc_info.value.details["entity"] == "summary"
    assert exc_info.value.details["celex"] == "32015L2366"


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
