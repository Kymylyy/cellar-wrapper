from __future__ import annotations

import pytest

from cellar_wrapper.errors import CellarParseError
from cellar_wrapper.subject_matter_index import (
    LocalSubjectMatterIndex,
    clear_subject_matter_index_cache,
    load_default_subject_matter_index,
)


def test_load_default_subject_matter_index_returns_searchable_entries() -> None:
    clear_subject_matter_index_cache()
    index = load_default_subject_matter_index()

    concept_uris = index.resolve_concept_uris(["data protection"])

    assert concept_uris
    assert any(uri.endswith("/PDON") for uri in concept_uris)


def test_resolve_concept_uris_is_case_insensitive_and_matches_concept_uri() -> None:
    index = LocalSubjectMatterIndex.from_json_payload(
        [
            {
                "concept_uri": "http://publications.europa.eu/resource/authority/subject-matter/PDON",
                "label": "Data protection",
            },
            {
                "concept_uri": "http://publications.europa.eu/resource/authority/subject-matter/SECR",
                "label": "Security system",
            },
        ],
        source_name="test",
    )

    concept_uris = index.resolve_concept_uris(["pdon", "DATA"])

    assert concept_uris == [
        "http://publications.europa.eu/resource/authority/subject-matter/PDON",
    ]


def test_resolve_concept_uris_deduplicates_concepts_across_codes() -> None:
    index = LocalSubjectMatterIndex.from_json_payload(
        [
            {
                "concept_uri": "http://publications.europa.eu/resource/authority/subject-matter/PDON",
                "label": "Data protection",
            },
            {
                "concept_uri": "http://publications.europa.eu/resource/authority/subject-matter/PDON",
                "label": "Protection of personal data",
            },
            {
                "concept_uri": "http://publications.europa.eu/resource/authority/subject-matter/SECR",
                "label": "Security system",
            },
        ],
        source_name="test",
    )

    concept_uris = index.resolve_concept_uris(["protection", "PDON"])

    assert concept_uris == [
        "http://publications.europa.eu/resource/authority/subject-matter/PDON",
    ]


@pytest.mark.parametrize(
    "payload",
    [
        {"concept_uri": "http://publications.europa.eu/resource/authority/subject-matter/PDON"},
        [{"concept_uri": "", "label": "Data protection"}],
        [{"concept_uri": "http://publications.europa.eu/resource/authority/subject-matter/PDON", "label": ""}],
        [{"concept_uri": "http://publications.europa.eu/resource/authority/subject-matter/PDON"}],
    ],
)
def test_from_json_payload_rejects_invalid_shapes(payload: object) -> None:
    with pytest.raises(CellarParseError):
        LocalSubjectMatterIndex.from_json_payload(payload, source_name="test")
