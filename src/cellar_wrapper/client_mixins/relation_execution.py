"""Relation query execution helpers shared by client mixins."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, cast

from cellar_wrapper.constants import MAX_LIMIT
from cellar_wrapper.errors import CellarValidationError
from cellar_wrapper.models import CaseLawItem, ListResult, NIMItem, RelationItem
from cellar_wrapper.parser import (
    parse_case_law_items,
    parse_nim_items,
    parse_relation_items,
)
from cellar_wrapper.sparql import build_relation_query

from .relation_specs import RELATION_CALL_SPECS, RelationCallSpec

BindingRow = dict[str, dict[str, str]]
ListResultBuilder = Callable[..., ListResult[Any]]
DateBound = date | datetime | str | None


@dataclass(frozen=True)
class RelationExecutionContext:
    """Bound client operations needed to execute relation-style queries."""

    validate_pagination: Callable[[int, int], None]
    normalize_celex: Callable[[str], str]
    normalize_lang: Callable[[str], str]
    normalize_resource_types: Callable[[Sequence[str] | None], list[str] | None]
    normalize_direction: Callable[[str | None], str | None]
    normalize_date_bounds: Callable[[DateBound, DateBound], tuple[str | None, str | None]]
    resolve_work_uri: Callable[[str], str]
    query_rows: Callable[[str], list[BindingRow]]
    list_result_builder: ListResultBuilder


def _date_sort_value(value: date | datetime | None) -> str:
    if value is None:
        return ""
    return value.isoformat()


def _first_non_null(items: list[NIMItem], attr: str) -> str | None:
    for item in items:
        value = getattr(item, attr)
        if value is not None:
            return cast(str, value)
    return None


def _group_nim_items(items: list[NIMItem], *, queried_celex: str) -> list[NIMItem]:
    preferred_prefix = f"7{queried_celex[1:]}"
    grouped_rows: dict[str, list[NIMItem]] = defaultdict(list)
    for item in items:
        grouped_rows[item.uri].append(item)

    grouped_items: list[NIMItem] = []
    for uri, group in grouped_rows.items():
        all_celexes = sorted({item.celex for item in group if item.celex is not None})
        matching_celexes = sorted({celex for celex in all_celexes if celex.startswith(preferred_prefix)})
        preferred_celex = matching_celexes[0] if matching_celexes else (all_celexes[0] if all_celexes else None)

        dated_values = [item.date for item in group if item.date is not None]
        max_date = max(dated_values, key=_date_sort_value) if dated_values else None
        title = next((item.title for item in group if item.title is not None), None)

        grouped_items.append(
            NIMItem(
                uri=uri,
                celex=preferred_celex,
                title=title,
                date=max_date,
                resource_type=_first_non_null(group, "resource_type"),
                direction=_first_non_null(group, "direction"),
                predicate=_first_non_null(group, "predicate"),
                relation_type=_first_non_null(group, "relation_type"),
                implemented_by_country=_first_non_null(group, "implemented_by_country"),
                all_celexes=all_celexes,
                matching_celexes=matching_celexes,
            )
        )

    grouped_items.sort(key=lambda item: ((item.implemented_by_country or ""), item.uri))
    grouped_items.sort(key=lambda item: _date_sort_value(item.date), reverse=True)
    return grouped_items


def fetch_relation_rows(
    *,
    context: RelationExecutionContext,
    method_name: str,
    celex: str,
    since: DateBound,
    to: DateBound,
    include_undated: bool,
    resource_types: Sequence[str] | None,
    limit: int,
    offset: int,
    lang: str,
    direction: str | None,
    include_implemented_by_country: bool,
) -> tuple[RelationCallSpec, list[BindingRow]]:
    spec = RELATION_CALL_SPECS.get(method_name)
    if spec is None:
        raise CellarValidationError(f"Unsupported relation method: {method_name}")

    context.validate_pagination(limit, offset)
    normalized_lang = context.normalize_lang(lang)
    normalized_types = context.normalize_resource_types(resource_types)
    if normalized_types is None and spec.default_resource_type is not None:
        normalized_types = [spec.default_resource_type]
    normalized_direction = context.normalize_direction(direction) or spec.direction
    since_value, to_value = context.normalize_date_bounds(since, to)
    work_uri = context.resolve_work_uri(celex)

    query = build_relation_query(
        work_uri,
        predicates=spec.predicates,
        direction=normalized_direction,
        since=since_value,
        to=to_value,
        resource_types=normalized_types,
        limit=limit,
        offset=offset,
        lang=normalized_lang,
        include_undated=include_undated,
        include_origin_country=spec.case_law,
        include_implemented_by_country=include_implemented_by_country,
    )
    return spec, context.query_rows(query)


def call_relation_result(
    *,
    context: RelationExecutionContext,
    method_name: str,
    celex: str,
    since: DateBound,
    to: DateBound,
    include_undated: bool,
    resource_types: Sequence[str] | None,
    limit: int,
    offset: int,
    lang: str,
    direction: str | None,
) -> ListResult[RelationItem] | ListResult[CaseLawItem]:
    spec, rows = fetch_relation_rows(
        context=context,
        method_name=method_name,
        celex=celex,
        since=since,
        to=to,
        include_undated=include_undated,
        resource_types=resource_types,
        limit=limit,
        offset=offset,
        lang=lang,
        direction=direction,
        include_implemented_by_country=False,
    )

    if spec.case_law:
        case_items = parse_case_law_items(rows)
        return cast(
            ListResult[CaseLawItem],
            context.list_result_builder(
                query_name=method_name,
                items=case_items,
                limit=limit,
                offset=offset,
            ),
        )

    relation_items = parse_relation_items(rows)
    return cast(
        ListResult[RelationItem],
        context.list_result_builder(
            query_name=method_name,
            items=relation_items,
            limit=limit,
            offset=offset,
        ),
    )


def call_nim_result(
    *,
    context: RelationExecutionContext,
    method_name: str,
    celex: str,
    since: DateBound,
    to: DateBound,
    include_undated: bool,
    resource_types: Sequence[str] | None,
    limit: int,
    offset: int,
    lang: str,
    direction: str | None,
) -> ListResult[NIMItem]:
    normalized_celex = context.normalize_celex(celex)
    all_rows: list[BindingRow] = []
    raw_offset = 0
    while True:
        _, rows = fetch_relation_rows(
            context=context,
            method_name=method_name,
            celex=normalized_celex,
            since=since,
            to=to,
            include_undated=include_undated,
            resource_types=resource_types,
            limit=MAX_LIMIT,
            offset=raw_offset,
            lang=lang,
            direction=direction,
            include_implemented_by_country=True,
        )
        all_rows.extend(rows)
        if len(rows) < MAX_LIMIT:
            break
        raw_offset += MAX_LIMIT

    nim_items = _group_nim_items(parse_nim_items(all_rows), queried_celex=normalized_celex)
    paginated_items = nim_items[offset : offset + limit]
    return cast(
        ListResult[NIMItem],
        context.list_result_builder(
            query_name=method_name,
            items=paginated_items,
            limit=limit,
            offset=offset,
        ),
    )
