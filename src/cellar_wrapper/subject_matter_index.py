"""Local subject-matter index for fast concept resolution."""

from __future__ import annotations

import json
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from typing import Any

from cellar_wrapper.errors import CellarParseError

_RESOURCE_PACKAGE = "cellar_wrapper.data"
_RESOURCE_NAME = "subject_matter_index.json"
_RESOURCE_PATH = f"{_RESOURCE_PACKAGE}/{_RESOURCE_NAME}"


@dataclass(frozen=True)
class _SubjectMatterEntry:
    concept_uri: str
    concept_uri_folded: str
    label: str
    label_folded: str


class LocalSubjectMatterIndex:
    """In-memory subject-matter concept index."""

    def __init__(self, entries: tuple[_SubjectMatterEntry, ...], *, source_name: str) -> None:
        self._entries = entries
        self._source_name = source_name

    @property
    def source_name(self) -> str:
        """Human-readable source descriptor for diagnostics."""
        return self._source_name

    def _iter_matching_entries(self, needle: str) -> Iterator[_SubjectMatterEntry]:
        for entry in self._entries:
            if needle in entry.concept_uri_folded or needle in entry.label_folded:
                yield entry

    @classmethod
    def from_json_payload(cls, payload: Any, *, source_name: str) -> LocalSubjectMatterIndex:
        """Build index from runtime JSON payload."""
        if not isinstance(payload, list):
            raise CellarParseError(
                "Local subject-matter index payload must be a JSON list",
                details={
                    "source": "local_subject_matter_index",
                    "phase": "validate_payload",
                    "source_name": source_name,
                    "payload_type": type(payload).__name__,
                },
            )

        seen_pairs: set[tuple[str, str]] = set()
        entries: list[_SubjectMatterEntry] = []

        for row_index, row in enumerate(payload):
            if not isinstance(row, dict):
                raise CellarParseError(
                    "Local subject-matter index row must be a JSON object",
                    details={
                        "source": "local_subject_matter_index",
                        "phase": "validate_row",
                        "source_name": source_name,
                        "row_index": row_index,
                        "row_type": type(row).__name__,
                    },
                )

            concept_uri = row.get("concept_uri")
            label = row.get("label")
            if not isinstance(concept_uri, str) or not concept_uri.strip():
                raise CellarParseError(
                    "Local subject-matter index row has invalid concept_uri",
                    details={
                        "source": "local_subject_matter_index",
                        "phase": "validate_row",
                        "source_name": source_name,
                        "row_index": row_index,
                    },
                )
            if not isinstance(label, str) or not label.strip():
                raise CellarParseError(
                    "Local subject-matter index row has invalid label",
                    details={
                        "source": "local_subject_matter_index",
                        "phase": "validate_row",
                        "source_name": source_name,
                        "row_index": row_index,
                        "concept_uri": concept_uri,
                    },
                )

            normalized_concept = concept_uri.strip()
            normalized_label = label.strip()
            key = (normalized_concept, normalized_label)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            entries.append(
                _SubjectMatterEntry(
                    concept_uri=normalized_concept,
                    concept_uri_folded=normalized_concept.casefold(),
                    label=normalized_label,
                    label_folded=normalized_label.casefold(),
                )
            )

        entries.sort(key=lambda entry: (entry.label, entry.concept_uri))
        return cls(tuple(entries), source_name=source_name)

    def resolve_concept_uris(self, codes: Sequence[str]) -> list[str]:
        """Resolve subject-matter textual codes to unique concept URIs with stable order."""
        concept_uris: list[str] = []
        seen_concepts: set[str] = set()

        for code in codes:
            needle = code.strip().casefold()
            if not needle:
                continue
            for entry in self._iter_matching_entries(needle):
                if entry.concept_uri in seen_concepts:
                    continue
                seen_concepts.add(entry.concept_uri)
                concept_uris.append(entry.concept_uri)

        return concept_uris


def _load_runtime_payload() -> Any:
    try:
        resource = resources.files(_RESOURCE_PACKAGE).joinpath(_RESOURCE_NAME)
        raw = resource.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        raise CellarParseError(
            "Failed to load local subject-matter index",
            details={
                "source": "local_subject_matter_index",
                "phase": "read_resource",
                "resource": _RESOURCE_PATH,
                "error_type": type(exc).__name__,
            },
        ) from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CellarParseError(
            "Failed to parse local subject-matter index JSON",
            details={
                "source": "local_subject_matter_index",
                "phase": "decode_json",
                "resource": _RESOURCE_PATH,
                "error": str(exc),
            },
        ) from exc


@lru_cache(maxsize=1)
def load_default_subject_matter_index() -> LocalSubjectMatterIndex:
    """Load default packaged subject-matter index (cached per-process)."""
    payload = _load_runtime_payload()
    return LocalSubjectMatterIndex.from_json_payload(payload, source_name=_RESOURCE_PATH)


def clear_subject_matter_index_cache() -> None:
    """Reset global index cache (useful for tests)."""
    load_default_subject_matter_index.cache_clear()
