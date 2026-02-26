from __future__ import annotations

from cellar_wrapper.client import CellarClient
from tests.helpers import FakeTransport, sparql_payload, sparql_row


def _resolver_payload() -> dict[str, object]:
    return sparql_payload(
        [
            sparql_row(
                work="http://publications.europa.eu/resource/cellar/act",
                celex="32022R2554",
            )
        ]
    )


def test_lookup_group_get_act() -> None:
    def query_handler(query: str) -> dict[str, object]:
        if "FILTER(UCASE(STR(?celex))" in query:
            return _resolver_payload()
        return sparql_payload(
            [
                sparql_row(
                    work="http://publications.europa.eu/resource/cellar/act",
                    celex="32022R2554",
                    eli="http://data.europa.eu/eli/reg/2022/2554/oj",
                    type="REG",
                    inForce="true",
                    dateDocument="2022-12-14",
                )
            ]
        )

    client = CellarClient(transport=FakeTransport(query_handler=query_handler))
    detail = client.get_act("32022R2554")
    assert detail.celex == "32022R2554"
    assert detail.in_force is True


def test_relations_group_get_amendments() -> None:
    def query_handler(query: str) -> dict[str, object]:
        if "FILTER(UCASE(STR(?celex))" in query:
            return _resolver_payload()
        return sparql_payload(
            [
                sparql_row(
                    other="http://publications.europa.eu/resource/cellar/other",
                    celex="32024R0886",
                    direction="incoming",
                    relationType="amends",
                )
            ]
        )

    client = CellarClient(transport=FakeTransport(query_handler=query_handler))
    result = client.get_amendments("32022R2554")
    assert result.returned_count == 1
    assert result.items[0].relation_type == "amends"


def test_lifecycle_group_get_dossier() -> None:
    def query_handler(query: str) -> dict[str, object]:
        if "FILTER(UCASE(STR(?celex))" in query:
            return _resolver_payload()
        return sparql_payload(
            [
                sparql_row(
                    other="http://publications.europa.eu/resource/cellar/proposal",
                    celex="52020PC0595",
                    relationType="dossier_contains_work",
                )
            ]
        )

    client = CellarClient(transport=FakeTransport(query_handler=query_handler))
    result = client.get_dossier("32022R2554")
    assert result.returned_count == 1


def test_case_law_group_get_cjeu_judgments() -> None:
    def query_handler(query: str) -> dict[str, object]:
        if "FILTER(UCASE(STR(?celex))" in query:
            return _resolver_payload()
        return sparql_payload(
            [
                sparql_row(
                    other="http://publications.europa.eu/resource/cellar/judgment",
                    celex="62019CJ0287",
                    ecli="ECLI:EU:C:2020:897",
                )
            ]
        )

    client = CellarClient(transport=FakeTransport(query_handler=query_handler))
    result = client.get_cjeu_judgments("32022R2554")
    assert result.returned_count == 1
    assert result.items[0].ecli == "ECLI:EU:C:2020:897"


def test_search_group_search_by_title() -> None:
    def query_handler(query: str) -> dict[str, object]:
        return sparql_payload(
            [
                sparql_row(
                    work="http://publications.europa.eu/resource/cellar/work",
                    celex="52023PC0367",
                    title="Proposal on payment services",
                )
            ]
        )

    client = CellarClient(transport=FakeTransport(query_handler=query_handler))
    result = client.search_by_title("payment")
    assert result.returned_count == 1


def test_monitoring_group_new_citations_adds_since_filter() -> None:
    transport = FakeTransport(query_handler=lambda query: _resolver_payload() if "FILTER(UCASE" in query else sparql_payload([]))
    client = CellarClient(transport=transport)
    result = client.new_citations("32022R2554", since="2025-01-01")
    assert result.returned_count == 0
    assert any("STR(?date) > '2025-01-01'" in query for query in transport.queries)


def test_download_group_get_text() -> None:
    def download_handler(url: str, accept: str, language: str | None) -> tuple[bytes, str, str]:
        return (b"abc", "application/pdf", url)

    client = CellarClient(transport=FakeTransport(download_handler=download_handler))
    payload = client.get_text("32022R2554", format="pdf")
    assert payload.content_type == "application/pdf"
    assert payload.content_base64 == "YWJj"
