"""Local EuroVoc index for fast concept resolution."""

from __future__ import annotations

import json
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from typing import Any

from cellar_wrapper.errors import CellarParseError
from cellar_wrapper.models import EurovocTag

LOCAL_EUROVOC_ENDPOINT = "local://eurovoc-index"
_RESOURCE_PACKAGE = "cellar_wrapper.data"
_RESOURCE_NAME = "eurovoc_index.json"
_RESOURCE_PATH = f"{_RESOURCE_PACKAGE}/{_RESOURCE_NAME}"


@dataclass(frozen=True)
class _EurovocEntry:
    concept_uri: str
    label: str
    label_folded: str


class LocalEurovocIndex:
    """In-memory EuroVoc concept index."""

    def __init__(self, entries: tuple[_EurovocEntry, ...], *, source_name: str) -> None:
        self._entries = entries
        self._source_name = source_name

    @property
    def source_name(self) -> str:
        """Human-readable source descriptor for diagnostics."""
        return self._source_name

    def _iter_matching_entries(self, needle: str) -> Iterator[_EurovocEntry]:
        for entry in self._entries:
            if needle in entry.label_folded:
                yield entry

    @classmethod
    def from_json_payload(cls, payload: Any, *, source_name: str) -> LocalEurovocIndex:
        """Build index from runtime JSON payload."""
        if not isinstance(payload, list):
            raise CellarParseError(
                "Local EuroVoc index payload must be a JSON list",
                details={
                    "source": "local_eurovoc_index",
                    "phase": "validate_payload",
                    "source_name": source_name,
                    "payload_type": type(payload).__name__,
                },
            )

        seen_pairs: set[tuple[str, str]] = set()
        entries: list[_EurovocEntry] = []

        for row_index, row in enumerate(payload):
            if not isinstance(row, dict):
                raise CellarParseError(
                    "Local EuroVoc index row must be a JSON object",
                    details={
                        "source": "local_eurovoc_index",
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
                    "Local EuroVoc index row has invalid concept_uri",
                    details={
                        "source": "local_eurovoc_index",
                        "phase": "validate_row",
                        "source_name": source_name,
                        "row_index": row_index,
                    },
                )
            if not isinstance(label, str) or not label.strip():
                raise CellarParseError(
                    "Local EuroVoc index row has invalid label",
                    details={
                        "source": "local_eurovoc_index",
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
                _EurovocEntry(
                    concept_uri=normalized_concept,
                    label=normalized_label,
                    label_folded=normalized_label.casefold(),
                )
            )

        entries.sort(key=lambda entry: (entry.label, entry.concept_uri))
        return cls(tuple(entries), source_name=source_name)

    def find_by_label(self, label: str, *, limit: int, offset: int) -> list[EurovocTag]:
        """Find EuroVoc concepts by case-insensitive substring match."""
        if limit <= 0:
            return []
        needle = label.strip().casefold()
        if not needle:
            return []

        matches: list[EurovocTag] = []
        skipped = 0
        for entry in self._iter_matching_entries(needle):
            if skipped < offset:
                skipped += 1
                continue
            matches.append(EurovocTag(concept_uri=entry.concept_uri, label=entry.label))
            if len(matches) >= limit:
                break
        return matches

    def resolve_concept_uris(self, tags: Sequence[str]) -> list[str]:
        """Resolve tag labels to unique concept URIs with stable order."""
        concept_uris: list[str] = []
        seen_concepts: set[str] = set()

        for tag in tags:
            needle = tag.strip().casefold()
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
            "Failed to load local EuroVoc index",
            details={
                "source": "local_eurovoc_index",
                "phase": "read_resource",
                "resource": _RESOURCE_PATH,
                "error_type": type(exc).__name__,
            },
        ) from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CellarParseError(
            "Failed to parse local EuroVoc index JSON",
            details={
                "source": "local_eurovoc_index",
                "phase": "decode_json",
                "resource": _RESOURCE_PATH,
                "error": str(exc),
            },
        ) from exc


@lru_cache(maxsize=1)
def load_default_eurovoc_index() -> LocalEurovocIndex:
    """Load default packaged EuroVoc index (cached per-process)."""
    payload = _load_runtime_payload()
    return LocalEurovocIndex.from_json_payload(payload, source_name=_RESOURCE_PATH)


def clear_eurovoc_index_cache() -> None:
    """Reset global index cache (useful for tests)."""
    load_default_eurovoc_index.cache_clear()
