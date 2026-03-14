"""Helpers to parse SPARQL JSON responses into typed models."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime
from typing import Any

from cellar_wrapper.date_utils import parse_iso_date_or_datetime
from cellar_wrapper.errors import CellarParseError
from cellar_wrapper.models import (
    ActDetail,
    ActRef,
    ArticleAnnotationItem,
    CaseLawItem,
    DossierItem,
    EurovocTag,
    ExpressionItem,
    NIMItem,
    RelationItem,
    SubjectMatterTag,
)

BindingRow = dict[str, dict[str, str]]


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
    if not isinstance(payload, dict):
        raise _parse_error(
            "SPARQL response payload is not an object",
            parser="parse_bindings",
            field="payload",
            value=payload,
        )

    try:
        results = payload["results"]
        if not isinstance(results, dict):
            raise TypeError("results must be an object")
        raw_bindings = results["bindings"]
    except (KeyError, TypeError) as exc:  # pragma: no cover - defensive guard
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


def _build_act_ref(
    row: BindingRow,
    *,
    parser: str,
    row_index: int,
    uri_key: str,
) -> ActRef:
    uri = value(row, uri_key)
    if uri is None:
        raise _parse_error(
            "SPARQL row missing required URI column",
            parser=parser,
            row_index=row_index,
            field=uri_key,
            value=row,
        )
    return ActRef(
        uri=uri,
        celex=value(row, "celex"),
        title=value(row, "title"),
        date=parse_date_value(value(row, "date"), field_name="date"),
        resource_type=value(row, "type"),
    )


def parse_date_value(raw: str | None, *, field_name: str) -> date | datetime | None:
    """Parse ISO date/datetime payload used by CELLAR fields."""
    if raw is None:
        return None

    candidate = raw.strip()
    if not candidate:
        return None

    try:
        return parse_iso_date_or_datetime(candidate)
    except ValueError as exc:
        raise _parse_error(
            f"Invalid date/datetime for {field_name}: {raw!r}",
            parser="parse_date_value",
            field=field_name,
            value=raw,
        ) from exc


def parse_bool_value(
    raw: str | None,
    *,
    parser: str,
    field_name: str,
    row_index: int | None = None,
) -> bool | None:
    """Parse optional bool values represented as true/false/1/0 strings."""
    if raw is None:
        return None
    normalized = raw.strip().lower()
    if normalized in {"true", "1"}:
        return True
    if normalized in {"false", "0"}:
        return False
    raise _parse_error(
        f"Invalid boolean for {field_name}",
        parser=parser,
        row_index=row_index,
        field=field_name,
        value=raw,
    )


def parse_act_refs(
    rows: list[BindingRow],
    *,
    uri_key: str = "uri",
) -> list[ActRef]:
    """Parse generic work rows into ActRef objects."""
    items: list[ActRef] = []
    for row_index, row in enumerate(rows):
        row = _ensure_binding_row(row, parser="parse_act_refs", row_index=row_index)
        items.append(_build_act_ref(row, parser="parse_act_refs", row_index=row_index, uri_key=uri_key))
    return items


def parse_uri_act_refs(rows: list[BindingRow]) -> list[ActRef]:
    """Parse list-query rows exposing the canonical ``?uri`` column."""
    return parse_act_refs(rows, uri_key="uri")


def _merge_scalar_value(
    values: dict[str, str | None],
    *,
    key: str,
    candidate: str | None,
    row_index: int,
) -> None:
    if candidate is None:
        return
    existing = values[key]
    if existing is None:
        values[key] = candidate
        return
    if existing != candidate:
        raise _parse_error(
            f"Conflicting scalar value for {key}",
            parser="parse_act_detail",
            row_index=row_index,
            field=key,
            value={"existing": existing, "candidate": candidate},
        )


def parse_act_detail(rows: list[BindingRow]) -> ActDetail | None:
    """Parse work-level detail query into ActDetail."""
    if not rows:
        return None

    normalized_rows = [
        _ensure_binding_row(row, parser="parse_act_detail", row_index=row_index)
        for row_index, row in enumerate(rows)
    ]
    work_uri = value(normalized_rows[0], "work")
    if work_uri is None:
        raise _parse_error(
            "get_act query returned row without work URI",
            parser="parse_act_detail",
            row_index=0,
            field="work",
            value=normalized_rows[0],
        )

    first_values: dict[str, str | None] = {
        "celex": None,
        "title": None,
        "type": None,
        "eli": None,
        "inForce": None,
        "eea": None,
        "dateDocument": None,
        "dateEntryIntoForce": None,
        "dateEndOfValidity": None,
    }
    created_by_agents: list[str] = []
    responsible_agents: list[str] = []
    addresses_institutions: list[str] = []
    signatory_names: list[str] = []
    created_by_seen: set[str] = set()
    responsible_seen: set[str] = set()
    addresses_seen: set[str] = set()
    signatories_seen: set[str] = set()

    for row_index, row in enumerate(normalized_rows):
        row_work_uri = value(row, "work")
        if row_work_uri != work_uri:
            raise _parse_error(
                "Conflicting work URI in act detail rows",
                parser="parse_act_detail",
                row_index=row_index,
                field="work",
                value={"expected": work_uri, "candidate": row_work_uri},
            )

        for key in first_values:
            _merge_scalar_value(
                first_values,
                key=key,
                candidate=value(row, key),
                row_index=row_index,
            )
        for key, target, seen in (
            ("createdBy", created_by_agents, created_by_seen),
            ("responsibleAgent", responsible_agents, responsible_seen),
            ("addressesInstitution", addresses_institutions, addresses_seen),
            ("signatoryName", signatory_names, signatories_seen),
        ):
            candidate = value(row, key)
            if candidate is not None and candidate not in seen:
                target.append(candidate)
                seen.add(candidate)

    in_force = parse_bool_value(
        first_values["inForce"],
        parser="parse_act_detail",
        field_name="inForce",
        row_index=0,
    )
    eea_relevant = parse_bool_value(
        first_values["eea"],
        parser="parse_act_detail",
        field_name="eea",
        row_index=0,
    )

    return ActDetail(
        uri=work_uri,
        celex=first_values["celex"],
        title=first_values["title"],
        resource_type=first_values["type"],
        eli=first_values["eli"],
        in_force=in_force,
        eea_relevant=eea_relevant,
        created_by_agents=created_by_agents,
        responsible_agents=responsible_agents,
        addresses_institutions=addresses_institutions,
        signatory_names=signatory_names,
        date_document=parse_date_value(
            first_values["dateDocument"],
            field_name="dateDocument",
        ),
        date_entry_into_force=parse_date_value(
            first_values["dateEntryIntoForce"],
            field_name="dateEntryIntoForce",
        ),
        date_end_of_validity=parse_date_value(
            first_values["dateEndOfValidity"],
            field_name="dateEndOfValidity",
        ),
    )


def _act_ref_rows(rows: list[BindingRow]) -> Iterable[tuple[ActRef, BindingRow]]:
    refs = parse_uri_act_refs(rows)
    return zip(refs, rows, strict=True)


def parse_relation_items(rows: list[BindingRow]) -> list[RelationItem]:
    """Parse relation queries to RelationItem list."""
    result: list[RelationItem] = []
    for ref, row in _act_ref_rows(rows):
        result.append(
            RelationItem(
                **ref.model_dump(),
                direction=value(row, "direction"),
                predicate=value(row, "predicate"),
                relation_type=value(row, "relationType"),
            )
        )
    return result


def parse_article_annotation_items(
    rows: list[BindingRow],
) -> list[ArticleAnnotationItem]:
    """Parse article-annotation queries to ArticleAnnotationItem list."""
    result: list[ArticleAnnotationItem] = []
    for ref, row in _act_ref_rows(rows):
        result.append(
            ArticleAnnotationItem(
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


def parse_case_law_items(rows: list[BindingRow]) -> list[CaseLawItem]:
    """Parse case-law rows."""
    result: list[CaseLawItem] = []
    for ref, row in _act_ref_rows(rows):
        result.append(
            CaseLawItem(
                **ref.model_dump(),
                ecli=value(row, "ecli"),
                court_formation=value(row, "courtFormation"),
                advocate_general=value(row, "advocateGeneral"),
                origin_country=value(row, "originCountry"),
            )
        )
    return result


def parse_dossier_items(rows: list[BindingRow]) -> list[DossierItem]:
    """Parse dossier query rows."""
    result: list[DossierItem] = []
    for row_index, (ref, row) in enumerate(_act_ref_rows(rows)):
        result.append(
            DossierItem(
                **ref.model_dump(),
                direction=value(row, "direction"),
                predicate=value(row, "predicate"),
                relation_type=value(row, "relationType"),
                dossier_uri=value(row, "dossier"),
                procedure_code=value(row, "procedureCode"),
                procedure_type=value(row, "procedureType"),
                status_adopted=parse_bool_value(
                    value(row, "statusAdopted"),
                    parser="parse_dossier_items",
                    field_name="statusAdopted",
                    row_index=row_index,
                ),
                status_pending=parse_bool_value(
                    value(row, "statusPending"),
                    parser="parse_dossier_items",
                    field_name="statusPending",
                    row_index=row_index,
                ),
                status_withdrawn=parse_bool_value(
                    value(row, "statusWithdrawn"),
                    parser="parse_dossier_items",
                    field_name="statusWithdrawn",
                    row_index=row_index,
                ),
                produces_act_uri=value(row, "producesAct"),
                produces_act_celex=value(row, "producesActCelex"),
            )
        )
    return result


def parse_nim_items(rows: list[BindingRow]) -> list[NIMItem]:
    """Parse NIM relation rows."""
    result: list[NIMItem] = []
    for ref, row in _act_ref_rows(rows):
        result.append(
            NIMItem(
                **ref.model_dump(),
                direction=value(row, "direction"),
                predicate=value(row, "predicate"),
                relation_type=value(row, "relationType"),
                implemented_by_country=value(row, "implementedByCountry"),
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
