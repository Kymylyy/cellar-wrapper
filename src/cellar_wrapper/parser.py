"""Helpers to parse SPARQL JSON responses into typed models."""

from __future__ import annotations

from typing import Any

from cellar_wrapper.errors import CellarParseError
from cellar_wrapper.models import (
    ActDetail,
    ActRef,
    CaseLawItem,
    EurovocTag,
    ExpressionItem,
    RelationItem,
    SubjectMatterTag,
)


def parse_bindings(payload: dict[str, Any]) -> list[dict[str, dict[str, str]]]:
    """Extract SPARQL bindings or raise a parse error."""
    try:
        raw_bindings = payload["results"]["bindings"]
    except KeyError as exc:  # pragma: no cover - defensive guard
        raise CellarParseError("SPARQL response missing results.bindings") from exc

    if not isinstance(raw_bindings, list):
        raise CellarParseError("SPARQL response has invalid bindings payload")
    return raw_bindings


def value(row: dict[str, dict[str, str]], key: str) -> str | None:
    """Return string value for a key in SPARQL binding row."""
    slot = row.get(key)
    if slot is None:
        return None
    return slot.get("value")


def parse_act_refs(rows: list[dict[str, dict[str, str]]]) -> list[ActRef]:
    """Parse generic work rows into ActRef objects."""
    items: list[ActRef] = []
    for row in rows:
        uri = (
            value(row, "work")
            or value(row, "other")
            or value(row, "act")
            or value(row, "uri")
            or value(row, "summary")
            or value(row, "opinion")
            or value(row, "dossier")
            or value(row, "item")
        )
        if uri is None:
            # Keep strict behavior for malformed rows.
            raise CellarParseError("Missing URI-like column in SPARQL row")

        items.append(
            ActRef(
                uri=uri,
                celex=value(row, "celex"),
                title=value(row, "title"),
                date=value(row, "date"),
                resource_type=value(row, "type"),
            )
        )
    return items


def parse_act_detail(rows: list[dict[str, dict[str, str]]]) -> ActDetail | None:
    """Parse work-level detail query into ActDetail."""
    if not rows:
        return None

    row = rows[0]
    uri = value(row, "work")
    if uri is None:
        raise CellarParseError("get_act query returned row without work URI")

    in_force_raw = value(row, "inForce")
    in_force: bool | None
    if in_force_raw is None:
        in_force = None
    else:
        in_force = in_force_raw.lower() in {"true", "1"}

    return ActDetail(
        uri=uri,
        celex=value(row, "celex"),
        title=value(row, "title"),
        resource_type=value(row, "type"),
        eli=value(row, "eli"),
        in_force=in_force,
        date_document=value(row, "dateDocument"),
        date_entry_into_force=value(row, "dateEntryIntoForce"),
        date_end_of_validity=value(row, "dateEndOfValidity"),
    )


def parse_relation_items(rows: list[dict[str, dict[str, str]]]) -> list[RelationItem]:
    """Parse relation queries to RelationItem list."""
    refs = parse_act_refs(rows)
    result: list[RelationItem] = []
    for ref, row in zip(refs, rows, strict=True):
        result.append(
            RelationItem(
                **ref.model_dump(),
                direction=value(row, "direction"),
                predicate=value(row, "predicate"),
                relation_type=value(row, "relationType"),
                annotation_uri=value(row, "annotation"),
                annotation_article=value(row, "article"),
                annotation_paragraph=value(row, "paragraph"),
                annotation_subparagraph=value(row, "subparagraph"),
                annotation_point=value(row, "point"),
                annotation_comment_on_legal_basis=value(row, "commentOnLegalBasis"),
            )
        )
    return result


def parse_case_law_items(rows: list[dict[str, dict[str, str]]]) -> list[CaseLawItem]:
    """Parse case-law rows."""
    refs = parse_act_refs(rows)
    result: list[CaseLawItem] = []
    for ref, row in zip(refs, rows, strict=True):
        result.append(
            CaseLawItem(
                **ref.model_dump(),
                ecli=value(row, "ecli"),
                court_formation=value(row, "courtFormation"),
                advocate_general=value(row, "advocateGeneral"),
            )
        )
    return result


def parse_eurovoc_tags(rows: list[dict[str, dict[str, str]]]) -> list[EurovocTag]:
    """Parse EuroVoc concepts."""
    tags: list[EurovocTag] = []
    for row in rows:
        concept_uri = value(row, "concept")
        if concept_uri is None:
            raise CellarParseError("EuroVoc query returned row without concept")
        tags.append(EurovocTag(concept_uri=concept_uri, label=value(row, "label")))
    return tags


def parse_subject_matter_tags(rows: list[dict[str, dict[str, str]]]) -> list[SubjectMatterTag]:
    """Parse subject-matter concepts."""
    tags: list[SubjectMatterTag] = []
    for row in rows:
        concept_uri = value(row, "concept")
        if concept_uri is None:
            raise CellarParseError("Subject-matter query returned row without concept")
        tags.append(SubjectMatterTag(concept_uri=concept_uri, label=value(row, "label")))
    return tags


def parse_expressions(rows: list[dict[str, dict[str, str]]]) -> list[ExpressionItem]:
    """Parse expression records."""
    expressions: list[ExpressionItem] = []
    for row in rows:
        expression_uri = value(row, "expression")
        if expression_uri is None:
            raise CellarParseError("Expression query returned row without expression URI")
        expressions.append(
            ExpressionItem(
                expression_uri=expression_uri,
                language_uri=value(row, "lang"),
                title=value(row, "title"),
            )
        )
    return expressions
