from __future__ import annotations

import inspect
from typing import Any

import pytest

from cellar_wrapper.cli_specs import COMMANDS
from cellar_wrapper.client import CellarClient
from cellar_wrapper.contract_specs import RETURN_CONTRACTS
from cellar_wrapper.errors import CellarValidationError
from cellar_wrapper.eurovoc_index import LOCAL_EUROVOC_ENDPOINT
from cellar_wrapper.models import ArticleAnnotationItem, ListResult, RelationItem
from tests.helpers import FakeTransport, sparql_payload, sparql_row


def _query_handler(query: str) -> dict[str, object]:
    if "FILTER(UCASE(STR(?celex))" in query:
        return sparql_payload(
            [
                sparql_row(
                    work="http://publications.europa.eu/resource/cellar/act",
                    celex="32022R2554",
                    title="Resolved act",
                )
            ]
        )

    if "SELECT DISTINCT ?summary WHERE" in query:
        return sparql_payload(
            [
                sparql_row(
                    summary="http://publications.europa.eu/resource/cellar/summary",
                )
            ]
        )

    if "SELECT DISTINCT ?work ?celex ?eli ?type ?inForce" in query:
        return sparql_payload(
            [
                sparql_row(
                    work="http://publications.europa.eu/resource/cellar/act",
                    celex="32022R2554",
                    eli="http://data.europa.eu/eli/reg/2022/2554/oj",
                    type="REG",
                    inForce="true",
                    dateDocument="2022-12-14",
                    dateEntryIntoForce="2023-01-16",
                    dateEndOfValidity="2099-12-31",
                    title="Digital operational resilience act",
                )
            ]
        )

    if "SELECT DISTINCT ?expression ?lang ?title" in query:
        return sparql_payload(
            [
                sparql_row(
                    expression="http://publications.europa.eu/resource/cellar/expression/eng",
                    lang="http://publications.europa.eu/resource/authority/language/ENG",
                    title="Expression title",
                )
            ]
        )

    if "SELECT DISTINCT ?concept ?label" in query:
        return sparql_payload(
            [
                sparql_row(
                    concept="http://eurovoc.europa.eu/1234",
                    label="payment services",
                )
            ]
        )

    if "SELECT DISTINCT ?work ?celex ?title ?date ?type" in query:
        return sparql_payload(
            [
                sparql_row(
                    work="http://publications.europa.eu/resource/cellar/work",
                    celex="52023PC0367",
                    title="Proposal on payment services",
                    date="2025-01-01",
                    type="PROP_REG",
                )
            ]
        )

    if "SELECT DISTINCT ?dossier ?other" in query:
        return sparql_payload(
            [
                sparql_row(
                    dossier="http://publications.europa.eu/resource/cellar/dossier",
                    other="http://publications.europa.eu/resource/cellar/related",
                    celex="52023PC0367",
                    title="Dossier item",
                    date="2025-01-01",
                    type="PROP_REG",
                    relationType="dossier_contains_work",
                    direction="incoming",
                    predicate="cdm:dossier_contains_work",
                )
            ]
        )

    if "owl:annotatedTarget" in query:
        return sparql_payload(
            [
                sparql_row(
                    other="http://publications.europa.eu/resource/cellar/annotated",
                    predicate="http://publications.europa.eu/ontology/cdm#resource_legal_amends_resource_legal",
                    relationType="article_annotation",
                    direction="incoming",
                    date="2025-01-01",
                    annotation="http://publications.europa.eu/resource/cellar/annotation",
                    article="5",
                    paragraph="1",
                    subparagraph="a",
                    point="i",
                    commentOnLegalBasis="reference note",
                )
            ]
        )

    if "directive_transposition" in query and "SELECT DISTINCT ?other ?celex ?date" in query:
        return sparql_payload(
            [
                sparql_row(
                    other="http://publications.europa.eu/resource/cellar/act",
                    celex="32022R2554",
                    date="2025-01-01",
                    relationType="deadline",
                    direction="outgoing",
                    predicate="cdm:resource_legal_date_deadline",
                )
            ]
        )

    if "resource_legal_proposes_to_amend_resource_legal" in query:
        return sparql_payload(
            [
                sparql_row(
                    other="http://publications.europa.eu/resource/cellar/related",
                    celex="52025PC1023",
                    title="Proposal for a REGULATION OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL amending Regulations (EU) 2017/745 and 2017/746",
                    date="2025-12-16T00:00:00",
                    relationType="proposes_to_change",
                    direction="incoming",
                    predicate="cdm:resource_legal_proposes_to_amend_resource_legal",
                )
            ]
        )

    return sparql_payload(
        [
            sparql_row(
                other="http://publications.europa.eu/resource/cellar/related",
                celex="32024R0001",
                title="Related item",
                date="2025-01-01",
                type="REG",
                direction="incoming",
                relationType="relation",
                predicate="cdm:work_related_to_work",
                ecli="ECLI:EU:C:2025:1",
                courtFormation="Grand Chamber",
                advocateGeneral="Advocate General",
            )
        ]
    )


def _download_handler(url: str, accept: str, _language: str | None) -> tuple[bytes, str, str]:
    return b"payload", accept, url


REQUIRED_ARG_VALUES: dict[str, Any] = {
    "celex": "32022R2554",
    "since": "2025-01-01",
    "tags": ["payment"],
    "codes": ["data protection"],
    "keyword": "payment",
    "dg": "FISMA",
    "label": "payment",
}

PUBLIC_METHODS = sorted({spec.method for spec in COMMANDS})


def _required_kwargs(method_name: str) -> dict[str, Any]:
    signature = inspect.signature(getattr(CellarClient, method_name))
    kwargs: dict[str, Any] = {}
    for parameter_name, parameter in signature.parameters.items():
        if parameter_name == "self":
            continue
        if parameter.default is inspect.Signature.empty:
            kwargs[parameter_name] = REQUIRED_ARG_VALUES[parameter_name]
    return kwargs


def test_public_methods_contract_definition_matches_client_surface() -> None:
    public_client_methods = {
        name
        for name, member in inspect.getmembers(CellarClient, predicate=inspect.isfunction)
        if not name.startswith("_") and name != "close"
    }
    assert public_client_methods == set(PUBLIC_METHODS)
    assert set(PUBLIC_METHODS) == set(RETURN_CONTRACTS)
    assert len(PUBLIC_METHODS) == 45


@pytest.mark.parametrize("method_name", PUBLIC_METHODS)
def test_public_methods_contract_runtime(method_name: str) -> None:
    client = CellarClient(
        transport=FakeTransport(
            query_handler=_query_handler,
            download_handler=_download_handler,
        )
    )
    kwargs = _required_kwargs(method_name)
    result = getattr(client, method_name)(**kwargs)
    contract = RETURN_CONTRACTS[method_name]

    if contract.return_type is ListResult:
        assert isinstance(result, ListResult)
        assert result.meta.query_name == contract.query_name
        assert result.returned_count == len(result.items)
        assert result.items
        assert contract.item_type is not None
        assert isinstance(result.items[0], contract.item_type)
    else:
        assert isinstance(result, contract.return_type)


def test_get_proposals_to_change_contract_emits_change_semantics() -> None:
    transport = FakeTransport(
        query_handler=_query_handler,
        download_handler=_download_handler,
    )
    client = CellarClient(transport=transport)

    result = client.get_proposals_to_change("32024R1689")

    assert result.meta.query_name == "get_proposals_to_change"
    assert result.items
    assert all(item.relation_type == "proposes_to_change" for item in result.items)


def test_new_proposals_to_change_contract_keeps_change_semantics() -> None:
    transport = FakeTransport(
        query_handler=_query_handler,
        download_handler=_download_handler,
    )
    client = CellarClient(transport=transport)

    result = client.new_proposals_to_change("32024R1689", "2025-01-01")

    assert result.meta.query_name == "new_proposals_to_change"
    assert result.items
    assert all(item.relation_type == "proposes_to_change" for item in result.items)


def test_non_monitoring_search_since_includes_undated_filter() -> None:
    transport = FakeTransport(query_handler=_query_handler, download_handler=_download_handler)
    client = CellarClient(transport=transport)

    _ = client.search_by_title("payment", since="2025-01-01")

    assert any(
        "FILTER(!BOUND(?date) || ?date > '2025-01-01T00:00:00Z'^^xsd:dateTime)" in query
        for query in transport.queries
    )


def test_non_monitoring_search_to_includes_upper_bound_filter() -> None:
    transport = FakeTransport(query_handler=_query_handler, download_handler=_download_handler)
    client = CellarClient(transport=transport)

    _ = client.search_by_title("payment", to="2025-02-01")

    assert any(
        "FILTER(!BOUND(?date) || ?date < '2025-02-01T00:00:00Z'^^xsd:dateTime)" in query
        for query in transport.queries
    )


def test_get_article_annotations_returns_article_annotation_items() -> None:
    transport = FakeTransport(query_handler=_query_handler, download_handler=_download_handler)
    client = CellarClient(transport=transport)

    result = client.get_article_annotations("32022R2554")

    assert result.items
    assert isinstance(result.items[0], ArticleAnnotationItem)
    assert result.items[0].annotation_uri == "http://publications.europa.eu/resource/cellar/annotation"
    assert result.items[0].annotation_article == "5"


def test_generic_relations_still_return_relation_items_without_annotation_fields() -> None:
    transport = FakeTransport(query_handler=_query_handler, download_handler=_download_handler)
    client = CellarClient(transport=transport)

    result = client.get_amendments("32022R2554")

    assert result.items
    assert isinstance(result.items[0], RelationItem)
    assert not hasattr(result.items[0], "annotation_uri")


def test_monitoring_since_is_strictly_date_bound() -> None:
    transport = FakeTransport(query_handler=_query_handler, download_handler=_download_handler)
    client = CellarClient(transport=transport)

    _ = client.new_case_law("32022R2554", since="2025-01-01")

    assert any(
        "FILTER(BOUND(?date) && ?date > '2025-01-01T00:00:00Z'^^xsd:dateTime)" in query
        for query in transport.queries
    )


def test_monitoring_combined_date_bounds_are_strict() -> None:
    transport = FakeTransport(query_handler=_query_handler, download_handler=_download_handler)
    client = CellarClient(transport=transport)

    _ = client.new_case_law("32022R2554", since="2025-01-01", to="2025-02-01")

    assert any(
        "FILTER(BOUND(?date) && (?date > '2025-01-01T00:00:00Z'^^xsd:dateTime && ?date < '2025-02-01T00:00:00Z'^^xsd:dateTime))"
        in query
        for query in transport.queries
    )


def test_inverted_date_range_raises_validation_error() -> None:
    client = CellarClient(
        transport=FakeTransport(
            query_handler=_query_handler,
            download_handler=_download_handler,
        )
    )

    with pytest.raises(CellarValidationError, match="since cannot be later than to"):
        client.search_by_title("payment", since="2025-02-01", to="2025-01-01")


def test_find_eurovoc_concept_uses_local_index_meta_endpoint() -> None:
    transport = FakeTransport(query_handler=_query_handler, download_handler=_download_handler)
    client = CellarClient(transport=transport)

    result = client.find_eurovoc_concept("payment", limit=5, offset=0)

    assert result.returned_count >= 1
    assert result.meta.endpoint == LOCAL_EUROVOC_ENDPOINT
    assert not any("SELECT DISTINCT ?concept ?label" in query for query in transport.queries)


def test_plural_alias_get_adopted_acts_matches_existing_method() -> None:
    transport = FakeTransport(query_handler=_query_handler, download_handler=_download_handler)
    client = CellarClient(transport=transport)

    singular = client.get_adopted_act("32022R2554")
    plural = client.get_adopted_acts("32022R2554")

    assert singular.items == plural.items
    assert singular.returned_count == plural.returned_count
