from __future__ import annotations

import pytest

from cellar_wrapper.errors import CellarParseError
from cellar_wrapper.eurovoc_index import (
    LocalEurovocIndex,
    clear_eurovoc_index_cache,
    load_default_eurovoc_index,
)


def test_load_default_eurovoc_index_returns_searchable_entries() -> None:
    clear_eurovoc_index_cache()
    index = load_default_eurovoc_index()

    results = index.find_by_label("payment", limit=10, offset=0)

    assert results
    assert any(item.label is not None and "payment" in item.label.casefold() for item in results)


def test_find_by_label_is_case_insensitive() -> None:
    index = LocalEurovocIndex.from_json_payload(
        [
            {"concept_uri": "http://eurovoc.europa.eu/1", "label": "Intra-EU Payment"},
            {"concept_uri": "http://eurovoc.europa.eu/2", "label": "Market access"},
        ],
        source_name="test",
    )

    results = index.find_by_label("PAYMENT", limit=10, offset=0)

    assert [item.concept_uri for item in results] == ["http://eurovoc.europa.eu/1"]


def test_find_by_label_applies_limit_and_offset_on_sorted_results() -> None:
    index = LocalEurovocIndex.from_json_payload(
        [
            {"concept_uri": "http://eurovoc.europa.eu/3", "label": "zeta payment"},
            {"concept_uri": "http://eurovoc.europa.eu/1", "label": "alpha payment"},
            {"concept_uri": "http://eurovoc.europa.eu/2", "label": "beta payment"},
        ],
        source_name="test",
    )

    page = index.find_by_label("payment", limit=1, offset=1)

    assert len(page) == 1
    assert page[0].concept_uri == "http://eurovoc.europa.eu/2"


def test_from_json_payload_deduplicates_identical_pairs() -> None:
    index = LocalEurovocIndex.from_json_payload(
        [
            {"concept_uri": "http://eurovoc.europa.eu/1", "label": "payment"},
            {"concept_uri": "http://eurovoc.europa.eu/1", "label": "payment"},
        ],
        source_name="test",
    )

    results = index.find_by_label("payment", limit=10, offset=0)

    assert len(results) == 1


def test_resolve_concept_uris_deduplicates_concepts_across_tags() -> None:
    index = LocalEurovocIndex.from_json_payload(
        [
            {"concept_uri": "http://eurovoc.europa.eu/1", "label": "payment"},
            {"concept_uri": "http://eurovoc.europa.eu/1", "label": "intra-EU payment"},
            {"concept_uri": "http://eurovoc.europa.eu/2", "label": "payment service"},
        ],
        source_name="test",
    )

    concept_uris = index.resolve_concept_uris(["payment", "service"])

    assert concept_uris == ["http://eurovoc.europa.eu/1", "http://eurovoc.europa.eu/2"]


@pytest.mark.parametrize(
    "payload",
    [
        {"concept_uri": "http://eurovoc.europa.eu/1", "label": "payment"},
        [{"concept_uri": "", "label": "payment"}],
        [{"concept_uri": "http://eurovoc.europa.eu/1", "label": ""}],
        [{"concept_uri": "http://eurovoc.europa.eu/1"}],
    ],
)
def test_from_json_payload_rejects_invalid_shapes(payload: object) -> None:
    with pytest.raises(CellarParseError):
        LocalEurovocIndex.from_json_payload(payload, source_name="test")
