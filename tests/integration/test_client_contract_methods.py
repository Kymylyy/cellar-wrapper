from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any

import pytest

from cellar_wrapper.cli_specs import COMMANDS
from cellar_wrapper.client import CellarClient
from cellar_wrapper.eurovoc_index import LOCAL_EUROVOC_ENDPOINT
from cellar_wrapper.models import (
    ActDetail,
    ActRef,
    CaseLawItem,
    DocumentPayload,
    DossierItem,
    EurovocTag,
    ExpressionItem,
    ListResult,
    NIMItem,
    RelationItem,
    SubjectMatterTag,
)
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
    "codes": ["06.30.10"],
    "keyword": "payment",
    "dg": "FISMA",
    "label": "payment",
}


@dataclass(frozen=True)
class ReturnContract:
    return_type: type[Any]
    item_type: type[Any] | None = None
    query_name: str | None = None


RELATION_METHODS = {
    "get_adopted_act",
    "get_ag_opinions",
    "get_amendments",
    "get_article_annotations",
    "get_citations",
    "get_completing_acts",
    "get_consolidated_versions",
    "get_corrigenda",
    "get_deadlines",
    "get_delegated_acts",
    "get_legal_basis",
    "get_opinions",
    "get_other_relations",
    "get_proposals_to_amend",
    "get_related_works",
    "get_repeals",
    "new_amendments",
    "new_citations",
    "new_consolidated",
    "new_corrigenda",
    "new_delegated_acts",
    "new_proposals_to_amend",
    "new_repeals",
}

CASE_METHODS = {
    "get_cjeu_judgments",
    "get_national_decisions",
    "get_preliminary_questions",
    "new_case_law",
    "new_preliminary_questions",
}

DOSSIER_METHODS = {"get_dossier"}
NIM_METHODS = {"get_nims", "new_nims"}
LOOKUP_CONCEPT_METHODS = {"get_eurovoc", "find_eurovoc_concept"}
SUBJECT_METHODS = {"get_subject_matter", "get_directory_codes"}
EXPRESSION_METHODS = {"get_expressions"}
ACT_SEARCH_METHODS = {
    "search_by_eurovoc",
    "search_by_subject_matter",
    "search_by_title",
    "search_communications",
    "new_by_eurovoc",
}


def _build_contracts() -> dict[str, ReturnContract]:
    contracts: dict[str, ReturnContract] = {
        "resolve_celex": ReturnContract(ActRef),
        "get_act": ReturnContract(ActDetail),
        "get_text": ReturnContract(DocumentPayload),
        "get_summary": ReturnContract(DocumentPayload),
    }
    for method_name in RELATION_METHODS:
        contracts[method_name] = ReturnContract(ListResult, item_type=RelationItem, query_name=method_name)
    for method_name in CASE_METHODS:
        contracts[method_name] = ReturnContract(ListResult, item_type=CaseLawItem, query_name=method_name)
    for method_name in DOSSIER_METHODS:
        contracts[method_name] = ReturnContract(ListResult, item_type=DossierItem, query_name=method_name)
    for method_name in NIM_METHODS:
        contracts[method_name] = ReturnContract(ListResult, item_type=NIMItem, query_name=method_name)
    for method_name in LOOKUP_CONCEPT_METHODS:
        contracts[method_name] = ReturnContract(ListResult, item_type=EurovocTag, query_name=method_name)
    for method_name in SUBJECT_METHODS:
        contracts[method_name] = ReturnContract(
            ListResult,
            item_type=SubjectMatterTag,
            query_name=method_name,
        )
    for method_name in EXPRESSION_METHODS:
        contracts[method_name] = ReturnContract(ListResult, item_type=ExpressionItem, query_name=method_name)
    for method_name in ACT_SEARCH_METHODS:
        contracts[method_name] = ReturnContract(ListResult, item_type=ActRef, query_name=method_name)
    return contracts


RETURN_CONTRACTS = _build_contracts()
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


def test_non_monitoring_search_since_includes_undated_filter() -> None:
    transport = FakeTransport(query_handler=_query_handler, download_handler=_download_handler)
    client = CellarClient(transport=transport)

    _ = client.search_by_title("payment", since="2025-01-01")

    assert any(
        "FILTER(!BOUND(?date) || ?date > '2025-01-01T00:00:00Z'^^xsd:dateTime)" in query
        for query in transport.queries
    )


def test_monitoring_since_is_strictly_date_bound() -> None:
    transport = FakeTransport(query_handler=_query_handler, download_handler=_download_handler)
    client = CellarClient(transport=transport)

    _ = client.new_case_law("32022R2554", since="2025-01-01")

    assert any(
        "FILTER(BOUND(?date) && ?date > '2025-01-01T00:00:00Z'^^xsd:dateTime)" in query
        for query in transport.queries
    )


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
