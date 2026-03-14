from __future__ import annotations

import pytest

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


def test_relations_group_get_amendments_direction_override() -> None:
    def query_handler(query: str) -> dict[str, object]:
        if "FILTER(UCASE(STR(?celex))" in query:
            return _resolver_payload()
        assert "BIND('outgoing' AS ?direction)" in query
        assert "BIND('incoming' AS ?direction)" not in query
        return sparql_payload(
            [
                sparql_row(
                    other="http://publications.europa.eu/resource/cellar/other",
                    celex="32011L0061",
                    direction="outgoing",
                    relationType="amends",
                )
            ]
        )

    client = CellarClient(transport=FakeTransport(query_handler=query_handler))
    result = client.get_amendments("32022R2554", direction="outgoing")
    assert result.returned_count == 1
    assert result.items[0].direction == "outgoing"


def test_lifecycle_group_get_dossier() -> None:
    def query_handler(query: str) -> dict[str, object]:
        if "FILTER(UCASE(STR(?celex))" in query:
            return _resolver_payload()
        return sparql_payload(
            [
                sparql_row(
                    other="http://publications.europa.eu/resource/cellar/proposal",
                    celex="52020PC0595",
                    dossier="http://publications.europa.eu/resource/cellar/dossier",
                    procedureCode="2023/0210/COD",
                    procedureType="OLP",
                    statusAdopted="0",
                    statusPending="1",
                    statusWithdrawn="0",
                    producesAct="http://publications.europa.eu/resource/cellar/final",
                    producesActCelex="32025R0001",
                    relationType="dossier_contains_work",
                )
            ]
        )

    client = CellarClient(transport=FakeTransport(query_handler=query_handler))
    result = client.get_dossier("32022R2554")
    assert result.returned_count == 1
    assert result.items[0].procedure_code == "2023/0210/COD"
    assert result.items[0].status_pending is True


def test_lifecycle_group_get_nims_exposes_country() -> None:
    def query_handler(query: str) -> dict[str, object]:
        if "FILTER(UCASE(STR(?celex))" in query:
            return _resolver_payload()
        return sparql_payload(
            [
                sparql_row(
                    other="http://publications.europa.eu/resource/cellar/nim",
                    celex="72015L2366POL_258600",
                    relationType="nims",
                    direction="incoming",
                    implementedByCountry="http://publications.europa.eu/resource/authority/country/POL",
                )
            ]
        )

    client = CellarClient(transport=FakeTransport(query_handler=query_handler))
    result = client.get_nims("32022R2554")
    assert result.returned_count == 1
    assert result.items[0].implemented_by_country is not None
    assert result.items[0].all_celexes == ["72015L2366POL_258600"]
    assert result.items[0].matching_celexes == []


def test_lifecycle_group_get_nims_regression_groups_omnibus_rows_by_uri() -> None:
    nim_uri = "http://publications.europa.eu/resource/cellar/nim-omnibus"

    def query_handler(query: str) -> dict[str, object]:
        if "FILTER(UCASE(STR(?celex))" in query:
            return sparql_payload(
                [
                    sparql_row(
                        work="http://publications.europa.eu/resource/cellar/act",
                        celex="32023L2225",
                    )
                ]
            )
        return sparql_payload(
            [
                sparql_row(
                    other=nim_uri,
                    celex="72014L0092HUN_202507032",
                    title="Hungarian omnibus implementation act",
                    date="2025-02-03",
                    relationType="nims",
                    direction="incoming",
                    predicate="cdm:measure_national_implementing_implements_resource_legal",
                    implementedByCountry="http://publications.europa.eu/resource/authority/country/HUN",
                ),
                sparql_row(
                    other=nim_uri,
                    celex="72023L2225HUN_202507032",
                    title="Hungarian omnibus implementation act",
                    date="2025-02-03",
                    relationType="nims",
                    direction="incoming",
                    predicate="cdm:measure_national_implementing_implements_resource_legal",
                    implementedByCountry="http://publications.europa.eu/resource/authority/country/HUN",
                ),
                sparql_row(
                    other=nim_uri,
                    celex="72024L0927HUN_202507032",
                    title="Hungarian omnibus implementation act",
                    date="2025-02-03",
                    relationType="nims",
                    direction="incoming",
                    predicate="cdm:measure_national_implementing_implements_resource_legal",
                    implementedByCountry="http://publications.europa.eu/resource/authority/country/HUN",
                ),
                sparql_row(
                    other=nim_uri,
                    celex="72023L2225HUN_202507032",
                    title="Hungarian omnibus implementation act",
                    date="2025-02-03",
                    relationType="nims",
                    direction="incoming",
                    predicate="cdm:measure_national_implementing_implements_resource_legal",
                    implementedByCountry="http://publications.europa.eu/resource/authority/country/HUN",
                ),
            ]
        )

    client = CellarClient(transport=FakeTransport(query_handler=query_handler))
    result = client.get_nims("32023L2225")

    assert result.returned_count == 1
    assert result.items[0].uri == nim_uri
    assert result.items[0].celex == "72023L2225HUN_202507032"
    assert result.items[0].all_celexes == [
        "72014L0092HUN_202507032",
        "72023L2225HUN_202507032",
        "72024L0927HUN_202507032",
    ]
    assert result.items[0].matching_celexes == ["72023L2225HUN_202507032"]
    assert result.items[0].implemented_by_country is not None


def test_lifecycle_group_get_nims_paginates_after_grouping() -> None:
    def query_handler(query: str) -> dict[str, object]:
        if "FILTER(UCASE(STR(?celex))" in query:
            return sparql_payload(
                [
                    sparql_row(
                        work="http://publications.europa.eu/resource/cellar/act",
                        celex="32015L2366",
                    )
                ]
            )
        return sparql_payload(
            [
                sparql_row(
                    other="http://publications.europa.eu/resource/cellar/nim-pol",
                    celex="72015L2366POL_258600",
                    date="2025-01-10",
                    implementedByCountry="http://publications.europa.eu/resource/authority/country/POL",
                ),
                sparql_row(
                    other="http://publications.europa.eu/resource/cellar/nim-hun",
                    celex="72014L0092HUN_202507032",
                    date="2025-03-01",
                    implementedByCountry="http://publications.europa.eu/resource/authority/country/HUN",
                ),
                sparql_row(
                    other="http://publications.europa.eu/resource/cellar/nim-deu",
                    celex="72015L2366DEU_202500001",
                    date="2025-03-01",
                    implementedByCountry="http://publications.europa.eu/resource/authority/country/DEU",
                ),
                sparql_row(
                    other="http://publications.europa.eu/resource/cellar/nim-hun",
                    celex="72015L2366HUN_202507032",
                    date="2025-03-01",
                    implementedByCountry="http://publications.europa.eu/resource/authority/country/HUN",
                ),
            ]
        )

    client = CellarClient(transport=FakeTransport(query_handler=query_handler))
    result = client.get_nims("32015L2366", limit=2, offset=1)

    assert result.returned_count == 2
    assert [item.uri for item in result.items] == [
        "http://publications.europa.eu/resource/cellar/nim-hun",
        "http://publications.europa.eu/resource/cellar/nim-pol",
    ]
    assert result.items[0].celex == "72015L2366HUN_202507032"
    assert result.items[0].matching_celexes == ["72015L2366HUN_202507032"]
    assert result.items[1].matching_celexes == ["72015L2366POL_258600"]


def test_lifecycle_group_get_corrigenda_defaults_to_corrigendum_type() -> None:
    def query_handler(query: str) -> dict[str, object]:
        if "FILTER(UCASE(STR(?celex))" in query:
            return _resolver_payload()
        assert "?other cdm:work_has_resource-type ?type ." in query
        assert (
            "VALUES ?type { "
            "<http://publications.europa.eu/resource/authority/resource-type/CORRIGENDUM> }"
            in query
        )
        return sparql_payload(
            [
                sparql_row(
                    other="http://publications.europa.eu/resource/cellar/corrigendum",
                    celex="32023R1114R(01)",
                    direction="incoming",
                    relationType="corrects",
                    type="http://publications.europa.eu/resource/authority/resource-type/CORRIGENDUM",
                )
            ]
        )

    client = CellarClient(transport=FakeTransport(query_handler=query_handler))
    result = client.get_corrigenda("32022R2554")
    assert result.returned_count == 1
    assert result.items[0].resource_type is not None
    assert result.items[0].resource_type.endswith("/CORRIGENDUM")


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


def test_case_law_group_get_national_decisions_country_filter() -> None:
    transport = FakeTransport(
        query_handler=lambda query: (
            _resolver_payload()
            if "FILTER(UCASE(STR(?celex))" in query
            else sparql_payload(
                [
                    sparql_row(
                        other="http://publications.europa.eu/resource/cellar/national-case",
                        celex="82021DE0115(51)",
                        originCountry="http://publications.europa.eu/resource/authority/country/DEU",
                    )
                ]
            )
        )
    )
    client = CellarClient(transport=transport)
    result = client.get_national_decisions("32022R2554", country="DEU")
    assert result.returned_count == 1
    assert result.items[0].origin_country is not None
    assert any("CONTAINS(UCASE(STR(?originCountry)), 'DEU')" in query for query in transport.queries)


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


def test_search_group_search_by_title_passes_resource_types_as_values_clause() -> None:
    transport = FakeTransport(
        query_handler=lambda _query: sparql_payload(
            [
                sparql_row(
                    work="http://publications.europa.eu/resource/cellar/work",
                    celex="32025R2263",
                    title="Crypto-assets",
                    type="REG_IMPL",
                )
            ]
        )
    )
    client = CellarClient(transport=transport)
    result = client.search_by_title("crypto-assets", resource_types=["REG_IMPL", "PUB_GEN"])

    assert result.returned_count == 1
    assert "OPTIONAL { ?work cdm:work_has_resource-type ?type }" not in transport.queries[0]
    assert "?work cdm:work_has_resource-type ?type ." in transport.queries[0]
    assert (
        "VALUES ?type { "
        "<http://publications.europa.eu/resource/authority/resource-type/REG_IMPL> "
        "<http://publications.europa.eu/resource/authority/resource-type/PUB_GEN> }"
        in transport.queries[0]
    )


def test_search_group_filtered_title_results_do_not_leak_sibling_types() -> None:
    def query_handler(query: str) -> dict[str, object]:
        if (
            "VALUES ?type { <http://publications.europa.eu/resource/authority/resource-type/PUB_GEN> }"
            in query
        ):
            return sparql_payload(
                [
                    sparql_row(
                        work="http://publications.europa.eu/resource/cellar/pub-gen",
                        celex="52024DC0001",
                        title="Crypto-assets communication",
                        type="PUB_GEN",
                    )
                ]
            )
        return sparql_payload(
            [
                sparql_row(
                    work="http://publications.europa.eu/resource/cellar/pub-gen",
                    celex="52024DC0001",
                    title="Crypto-assets communication",
                    type="PUB_GEN",
                ),
                sparql_row(
                    work="http://publications.europa.eu/resource/cellar/sibling",
                    celex="52024SC0001",
                    title="Crypto-assets staff working document",
                    type="STU",
                ),
            ]
        )

    transport = FakeTransport(query_handler=query_handler)
    client = CellarClient(transport=transport)

    result = client.search_by_title("crypto-assets", resource_types=["PUB_GEN"])

    assert result.returned_count == 1
    assert [item.celex for item in result.items] == ["52024DC0001"]
    assert all(item.resource_type in {"PUB_GEN", "http://publications.europa.eu/resource/authority/resource-type/PUB_GEN"} for item in result.items)
    assert (
        "VALUES ?type { <http://publications.europa.eu/resource/authority/resource-type/PUB_GEN> }"
        in transport.queries[0]
    )


def test_search_group_search_by_eurovoc_resolves_tags_before_search(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def query_handler(_query: str) -> dict[str, object]:
        return sparql_payload(
            [
                sparql_row(
                    work="http://publications.europa.eu/resource/cellar/work",
                    celex="52023PC0367",
                    title="Proposal on payment services",
                )
            ]
        )

    transport = FakeTransport(query_handler=query_handler)
    client = CellarClient(transport=transport)
    monkeypatch.setattr(
        client,
        "_resolve_eurovoc_concept_uris",
        lambda tags: ["http://eurovoc.europa.eu/2220"] if tags else [],
    )
    result = client.search_by_eurovoc(["payment"], since="2025-01-01")

    assert result.returned_count == 1
    assert len(transport.queries) == 1
    assert "VALUES ?concept { <http://eurovoc.europa.eu/2220> }" in transport.queries[0]
    assert "FILTER(!BOUND(?date) || ?date > '2025-01-01T00:00:00Z'^^xsd:dateTime)" in transport.queries[0]


def test_search_group_search_by_eurovoc_passes_resource_types_as_values_clause(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = FakeTransport(query_handler=lambda _query: sparql_payload([]))
    client = CellarClient(transport=transport)
    monkeypatch.setattr(
        client,
        "_resolve_eurovoc_concept_uris",
        lambda tags: ["http://eurovoc.europa.eu/2220"] if tags else [],
    )

    _ = client.search_by_eurovoc(["financial services"], resource_types=["PROP_REG", "PROP_DIR"])

    assert "?work cdm:work_has_resource-type ?type ." in transport.queries[0]
    assert (
        "VALUES ?type { "
        "<http://publications.europa.eu/resource/authority/resource-type/PROP_REG> "
        "<http://publications.europa.eu/resource/authority/resource-type/PROP_DIR> }"
        in transport.queries[0]
    )


def test_search_group_search_by_eurovoc_supports_upper_bound_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = FakeTransport(query_handler=lambda _query: sparql_payload([]))
    client = CellarClient(transport=transport)
    monkeypatch.setattr(
        client,
        "_resolve_eurovoc_concept_uris",
        lambda tags: ["http://eurovoc.europa.eu/2220"] if tags else [],
    )

    _ = client.search_by_eurovoc(["payment"], to="2025-02-01")

    assert "FILTER(!BOUND(?date) || ?date < '2025-02-01T00:00:00Z'^^xsd:dateTime)" in transport.queries[0]


def test_search_group_search_by_eurovoc_returns_empty_when_no_concept_resolved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = FakeTransport(query_handler=lambda _query: sparql_payload([]))
    client = CellarClient(transport=transport)
    monkeypatch.setattr(client, "_resolve_eurovoc_concept_uris", lambda tags: [])
    result = client.search_by_eurovoc(["unknown-term"])

    assert result.returned_count == 0
    assert len(transport.queries) == 0


def test_search_group_search_by_subject_matter_passes_resource_types_as_values_clause(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = FakeTransport(query_handler=lambda _query: sparql_payload([]))
    client = CellarClient(transport=transport)
    monkeypatch.setattr(
        client,
        "_resolve_subject_matter_concept_uris",
        lambda codes: ["http://publications.europa.eu/resource/authority/subject-matter/PDON"] if codes else [],
    )

    _ = client.search_by_subject_matter(
        ["bank"],
        resource_types=["DEC", "OPIN_DRAFT_NATION_LEGIS"],
    )

    assert (
        "VALUES ?type { "
        "<http://publications.europa.eu/resource/authority/resource-type/DEC> "
        "<http://publications.europa.eu/resource/authority/resource-type/OPIN_DRAFT_NATION_LEGIS> }"
        in transport.queries[0]
    )


def test_monitoring_group_new_citations_adds_since_filter() -> None:
    transport = FakeTransport(query_handler=lambda query: _resolver_payload() if "FILTER(UCASE" in query else sparql_payload([]))
    client = CellarClient(transport=transport)
    result = client.new_citations("32022R2554", since="2025-01-01")
    assert result.returned_count == 0
    assert any(
        "FILTER(BOUND(?date) && ?date > '2025-01-01T00:00:00Z'^^xsd:dateTime)" in query
        for query in transport.queries
    )


def test_monitoring_group_new_based_on_acts_uses_based_on_predicate() -> None:
    transport = FakeTransport(query_handler=lambda query: _resolver_payload() if "FILTER(UCASE" in query else sparql_payload([]))
    client = CellarClient(transport=transport)
    result = client.new_based_on_acts("32022R2554", since="2025-01-01")

    assert result.returned_count == 0
    relation_queries = [query for query in transport.queries if "resource_legal_based_on_resource_legal" in query]
    assert relation_queries
    assert "FILTER(BOUND(?date) && ?date > '2025-01-01T00:00:00Z'^^xsd:dateTime)" in relation_queries[0]


def test_monitoring_group_new_corrigenda_defaults_to_corrigendum_type() -> None:
    transport = FakeTransport(query_handler=lambda query: _resolver_payload() if "FILTER(UCASE" in query else sparql_payload([]))
    client = CellarClient(transport=transport)
    result = client.new_corrigenda("32022R2554", since="2025-01-01")

    assert result.returned_count == 0
    relation_queries = [query for query in transport.queries if "resource_legal_corrects_resource_legal" in query]
    assert relation_queries
    assert "?other cdm:work_has_resource-type ?type ." in relation_queries[0]
    assert (
        "VALUES ?type { "
        "<http://publications.europa.eu/resource/authority/resource-type/CORRIGENDUM> }"
        in relation_queries[0]
    )
    assert "FILTER(BOUND(?date) && ?date > '2025-01-01T00:00:00Z'^^xsd:dateTime)" in relation_queries[0]


def test_monitoring_group_new_nims_groups_rows_and_applies_strict_since() -> None:
    nim_uri = "http://publications.europa.eu/resource/cellar/nim-fin"

    def query_handler(query: str) -> dict[str, object]:
        if "FILTER(UCASE(STR(?celex))" in query:
            return sparql_payload(
                [
                    sparql_row(
                        work="http://publications.europa.eu/resource/cellar/act",
                        celex="32023L2225",
                    )
                ]
            )
        return sparql_payload(
            [
                sparql_row(
                    other=nim_uri,
                    celex="72023L2225FIN_202600932",
                    date="2026-02-04",
                    relationType="nims",
                    direction="incoming",
                    predicate="cdm:measure_national_implementing_implements_resource_legal",
                    implementedByCountry="http://publications.europa.eu/resource/authority/country/FIN",
                ),
                sparql_row(
                    other=nim_uri,
                    celex="72024L1619FIN_202600932",
                    date="2026-02-04",
                    relationType="nims",
                    direction="incoming",
                    predicate="cdm:measure_national_implementing_implements_resource_legal",
                    implementedByCountry="http://publications.europa.eu/resource/authority/country/FIN",
                ),
            ]
        )

    transport = FakeTransport(query_handler=query_handler)
    client = CellarClient(transport=transport)
    result = client.new_nims("32023L2225", since="2025-01-01")

    assert result.returned_count == 1
    assert result.items[0].uri == nim_uri
    assert result.items[0].celex == "72023L2225FIN_202600932"
    assert result.items[0].all_celexes == [
        "72023L2225FIN_202600932",
        "72024L1619FIN_202600932",
    ]
    assert result.items[0].matching_celexes == ["72023L2225FIN_202600932"]
    assert any(
        "FILTER(BOUND(?date) && ?date > '2025-01-01T00:00:00Z'^^xsd:dateTime)" in query
        for query in transport.queries
    )


def test_monitoring_group_new_by_eurovoc_uses_strict_since_after_resolve(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def query_handler(_query: str) -> dict[str, object]:
        return sparql_payload([])

    transport = FakeTransport(query_handler=query_handler)
    client = CellarClient(transport=transport)
    monkeypatch.setattr(
        client,
        "_resolve_eurovoc_concept_uris",
        lambda tags: ["http://eurovoc.europa.eu/2220"] if tags else [],
    )
    result = client.new_by_eurovoc(["payment"], since="2025-01-01")

    assert result.returned_count == 0
    assert len(transport.queries) == 1
    assert "VALUES ?concept { <http://eurovoc.europa.eu/2220> }" in transport.queries[0]
    assert "FILTER(BOUND(?date) && ?date > '2025-01-01T00:00:00Z'^^xsd:dateTime)" in transport.queries[0]


def test_monitoring_group_new_by_eurovoc_passes_resource_types_as_values_clause(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = FakeTransport(query_handler=lambda _query: sparql_payload([]))
    client = CellarClient(transport=transport)
    monkeypatch.setattr(
        client,
        "_resolve_eurovoc_concept_uris",
        lambda tags: ["http://eurovoc.europa.eu/2220"] if tags else [],
    )

    _ = client.new_by_eurovoc(
        ["financial services"],
        since="2025-01-01",
        resource_types=["PROP_REG", "PROP_DIR"],
    )

    assert (
        "VALUES ?type { "
        "<http://publications.europa.eu/resource/authority/resource-type/PROP_REG> "
        "<http://publications.europa.eu/resource/authority/resource-type/PROP_DIR> }"
        in transport.queries[0]
    )


def test_non_monitoring_since_filter_keeps_undated_rows() -> None:
    transport = FakeTransport(query_handler=lambda query: _resolver_payload() if "FILTER(UCASE" in query else sparql_payload([]))
    client = CellarClient(transport=transport)
    result = client.get_amendments("32022R2554", since="2025-01-01")
    assert result.returned_count == 0
    assert any(
        "FILTER(!BOUND(?date) || ?date > '2025-01-01T00:00:00Z'^^xsd:dateTime)" in query
        for query in transport.queries
    )


def test_relations_group_get_based_on_acts_uses_based_on_predicate() -> None:
    transport = FakeTransport(query_handler=lambda query: _resolver_payload() if "FILTER(UCASE" in query else sparql_payload([]))
    client = CellarClient(transport=transport)
    result = client.get_based_on_acts("32022R2554", since="2025-01-01")

    assert result.returned_count == 0
    relation_queries = [query for query in transport.queries if "resource_legal_based_on_resource_legal" in query]
    assert relation_queries
    assert "FILTER(!BOUND(?date) || ?date > '2025-01-01T00:00:00Z'^^xsd:dateTime)" in relation_queries[0]


def test_non_monitoring_combined_date_bounds_keep_undated_rows() -> None:
    transport = FakeTransport(query_handler=lambda query: _resolver_payload() if "FILTER(UCASE" in query else sparql_payload([]))
    client = CellarClient(transport=transport)

    _ = client.get_amendments("32022R2554", since="2025-01-01", to="2025-02-01")

    assert any(
        "FILTER(!BOUND(?date) || (?date > '2025-01-01T00:00:00Z'^^xsd:dateTime && ?date < '2025-02-01T00:00:00Z'^^xsd:dateTime))"
        in query
        for query in transport.queries
    )


def test_lookup_group_get_eurovoc_applies_limit_offset() -> None:
    def query_handler(query: str) -> dict[str, object]:
        if "FILTER(UCASE(STR(?celex))" in query:
            return _resolver_payload()
        return sparql_payload([])

    transport = FakeTransport(query_handler=query_handler)
    client = CellarClient(transport=transport)
    _ = client.get_eurovoc("32022R2554", limit=7, offset=9)
    concept_queries = [query for query in transport.queries if "work_is_about_concept_eurovoc" in query]
    assert concept_queries
    assert "LIMIT 7" in concept_queries[0]
    assert "OFFSET 9" in concept_queries[0]


def test_download_group_get_text() -> None:
    def query_handler(query: str) -> dict[str, object]:
        if "FILTER(UCASE(STR(?celex))" in query:
            return _resolver_payload()
        return sparql_payload([])

    def download_handler(url: str, accept: str, language: str | None) -> tuple[bytes, str, str]:
        return (b"abc", "application/pdf", url)

    client = CellarClient(
        transport=FakeTransport(query_handler=query_handler, download_handler=download_handler)
    )
    payload = client.get_text("32022R2554", format="pdf")
    assert payload.content_type == "application/pdf"
    assert payload.content_base64 == "YWJj"
