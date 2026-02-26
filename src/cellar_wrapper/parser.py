"""Helpers to parse SPARQL JSON responses into typed models."""

from __future__ import annotations

from datetime import date, datetime
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


def _value_excerpt(value: Any, *, limit: int = 120) -> str:
    text = repr(value)
    if len(text) <= limit:
        return text
    return f"{text[:limit]}..."


def _parse_error(
    message: str,
    *,
    parser: str,
    row_index: int | None = None,
    field: str | None = None,
    value: Any = None,
) -> CellarParseError:
    details: dict[str, Any] = {"parser": parser}
    if row_index is not None:
        details["row_index"] = row_index
    if field is not None:
        details["field"] = field
    if value is not None:
        details["value_excerpt"] = _value_excerpt(value)
    return CellarParseError(message, details=details)


def _ensure_binding_row(row: Any, *, parser: str, row_index: int) -> dict[str, dict[str, str]]:
    if not isinstance(row, dict):
        raise _parse_error(
            "SPARQL row is not an object",
            parser=parser,
            row_index=row_index,
            field="row",
            value=row,
        )
    for key, slot in row.items():
        if not isinstance(key, str):
            raise _parse_error(
                "SPARQL row key is not a string",
                parser=parser,
                row_index=row_index,
                field="row_key",
                value=key,
            )
        if not isinstance(slot, dict):
            raise _parse_error(
                "SPARQL row binding slot is not an object",
                parser=parser,
                row_index=row_index,
                field=key,
                value=slot,
            )
        slot_value = slot.get("value")
        if slot_value is not None and not isinstance(slot_value, str):
            raise _parse_error(
                "SPARQL row binding slot value is not a string",
                parser=parser,
                row_index=row_index,
                field=key,
                value=slot,
            )
    return row


def parse_bindings(payload: dict[str, Any]) -> list[dict[str, dict[str, str]]]:
    """Extract SPARQL bindings or raise a parse error."""
    try:
        raw_bindings = payload["results"]["bindings"]
    except KeyError as exc:  # pragma: no cover - defensive guard
        raise _parse_error(
            "SPARQL response missing results.bindings",
            parser="parse_bindings",
            field="results.bindings",
            value=payload,
        ) from exc

    if not isinstance(raw_bindings, list):
        raise _parse_error(
            "SPARQL response has invalid bindings payload",
            parser="parse_bindings",
            field="results.bindings",
            value=raw_bindings,
        )
    return raw_bindings


def value(row: dict[str, dict[str, str]], key: str) -> str | None:
    """Return string value for a key in SPARQL binding row."""
    slot = row.get(key)
    if slot is None:
        return None
    return slot.get("value")


def parse_date_value(raw: str | None, *, field_name: str) -> date | datetime | None:
    """Parse ISO date/datetime payload used by CELLAR fields."""
    if raw is None:
        return None

    candidate = raw.strip()
    if not candidate:
        return None

    candidate_for_datetime = candidate.replace("Z", "+00:00")
    if "T" in candidate_for_datetime.upper():
        try:
            return datetime.fromisoformat(candidate_for_datetime)
        except ValueError as exc:
            raise _parse_error(
                f"Invalid datetime for {field_name}: {raw!r}",
                parser="parse_date_value",
                field=field_name,
                value=raw,
            ) from exc

    try:
        return date.fromisoformat(candidate)
    except ValueError:
        try:
            return datetime.fromisoformat(candidate_for_datetime)
        except ValueError as exc:
            raise _parse_error(
                f"Invalid date for {field_name}: {raw!r}",
                parser="parse_date_value",
                field=field_name,
                value=raw,
            ) from exc


def parse_act_refs(rows: list[dict[str, dict[str, str]]]) -> list[ActRef]:
    """Parse generic work rows into ActRef objects."""
    items: list[ActRef] = []
    for row_index, row in enumerate(rows):
        row = _ensure_binding_row(row, parser="parse_act_refs", row_index=row_index)
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
            raise _parse_error(
                "Missing URI-like column in SPARQL row",
                parser="parse_act_refs",
                row_index=row_index,
                field="work|other|act|uri|summary|opinion|dossier|item",
                value=row,
            )

        items.append(
            ActRef(
                uri=uri,
                celex=value(row, "celex"),
                title=value(row, "title"),
                date=parse_date_value(value(row, "date"), field_name="date"),
                resource_type=value(row, "type"),
            )
        )
    return items


def parse_act_detail(rows: list[dict[str, dict[str, str]]]) -> ActDetail | None:
    """Parse work-level detail query into ActDetail."""
    if not rows:
        return None

    row = _ensure_binding_row(rows[0], parser="parse_act_detail", row_index=0)
    uri = value(row, "work")
    if uri is None:
        raise _parse_error(
            "get_act query returned row without work URI",
            parser="parse_act_detail",
            row_index=0,
            field="work",
            value=row,
        )

    in_force_raw = value(row, "inForce")
    in_force: bool | None
    if in_force_raw is None:
        in_force = None
    else:
        normalized_bool = in_force_raw.strip().lower()
        if normalized_bool in {"true", "1"}:
            in_force = True
        elif normalized_bool in {"false", "0"}:
            in_force = False
        else:
            raise _parse_error(
                "Invalid boolean for inForce field",
                parser="parse_act_detail",
                row_index=0,
                field="inForce",
                value=in_force_raw,
            )

    return ActDetail(
        uri=uri,
        celex=value(row, "celex"),
        title=value(row, "title"),
        resource_type=value(row, "type"),
        eli=value(row, "eli"),
        in_force=in_force,
        date_document=parse_date_value(value(row, "dateDocument"), field_name="dateDocument"),
        date_entry_into_force=parse_date_value(
            value(row, "dateEntryIntoForce"),
            field_name="dateEntryIntoForce",
        ),
        date_end_of_validity=parse_date_value(
            value(row, "dateEndOfValidity"),
            field_name="dateEndOfValidity",
        ),
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
    for row_index, row in enumerate(rows):
        row = _ensure_binding_row(row, parser="parse_eurovoc_tags", row_index=row_index)
        concept_uri = value(row, "concept")
        if concept_uri is None:
            raise _parse_error(
                "EuroVoc query returned row without concept",
                parser="parse_eurovoc_tags",
                row_index=row_index,
                field="concept",
                value=row,
            )
        tags.append(EurovocTag(concept_uri=concept_uri, label=value(row, "label")))
    return tags


def parse_subject_matter_tags(rows: list[dict[str, dict[str, str]]]) -> list[SubjectMatterTag]:
    """Parse subject-matter concepts."""
    tags: list[SubjectMatterTag] = []
    for row_index, row in enumerate(rows):
        row = _ensure_binding_row(row, parser="parse_subject_matter_tags", row_index=row_index)
        concept_uri = value(row, "concept")
        if concept_uri is None:
            raise _parse_error(
                "Subject-matter query returned row without concept",
                parser="parse_subject_matter_tags",
                row_index=row_index,
                field="concept",
                value=row,
            )
        tags.append(SubjectMatterTag(concept_uri=concept_uri, label=value(row, "label")))
    return tags


def parse_expressions(rows: list[dict[str, dict[str, str]]]) -> list[ExpressionItem]:
    """Parse expression records."""
    expressions: list[ExpressionItem] = []
    for row_index, row in enumerate(rows):
        row = _ensure_binding_row(row, parser="parse_expressions", row_index=row_index)
        expression_uri = value(row, "expression")
        if expression_uri is None:
            raise _parse_error(
                "Expression query returned row without expression URI",
                parser="parse_expressions",
                row_index=row_index,
                field="expression",
                value=row,
            )
        expressions.append(
            ExpressionItem(
                expression_uri=expression_uri,
                language_uri=value(row, "lang"),
                title=value(row, "title"),
            )
        )
    return expressions
