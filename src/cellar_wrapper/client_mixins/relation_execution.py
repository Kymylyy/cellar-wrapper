"""Relation query execution helpers shared by client mixins."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime
from typing import Any, cast

from cellar_wrapper.errors import CellarValidationError
from cellar_wrapper.models import CaseLawItem, ListResult, NIMItem, RelationItem
from cellar_wrapper.parser import (
    parse_bindings,
    parse_case_law_items,
    parse_nim_items,
    parse_relation_items,
)
from cellar_wrapper.sparql import build_relation_query

from .relation_specs import RELATION_CALL_SPECS, RelationCallSpec

BindingRow = dict[str, dict[str, str]]
QueryFn = Callable[[str], dict[str, Any]]
ListResultBuilder = Callable[..., ListResult[Any]]


def fetch_relation_rows(
    *,
    method_name: str,
    celex: str,
    since: date | datetime | str | None,
    to: date | datetime | str | None,
    include_undated: bool,
    resource_type: str | None,
    limit: int,
    offset: int,
    lang: str,
    direction: str | None,
    include_implemented_by_country: bool,
    validate_pagination: Callable[[int, int], None],
    normalize_lang: Callable[[str], str],
    normalize_resource_type: Callable[[str | None], str | None],
    normalize_direction: Callable[[str | None], str | None],
    normalize_date_bounds: Callable[
        [date | datetime | str | None, date | datetime | str | None],
        tuple[str | None, str | None],
    ],
    resolve_work_uri: Callable[[str], str],
    query_sparql: QueryFn,
) -> tuple[RelationCallSpec, list[BindingRow]]:
    spec = RELATION_CALL_SPECS.get(method_name)
    if spec is None:
        raise CellarValidationError(f"Unsupported relation method: {method_name}")

    validate_pagination(limit, offset)
    normalized_lang = normalize_lang(lang)
    normalized_type = normalize_resource_type(resource_type) or spec.default_resource_type
    normalized_direction = normalize_direction(direction) or spec.direction
    since_value, to_value = normalize_date_bounds(since, to)
    work_uri = resolve_work_uri(celex)

    query = build_relation_query(
        work_uri,
        predicates=spec.predicates,
        direction=normalized_direction,
        since=since_value,
        to=to_value,
        resource_type=normalized_type,
        limit=limit,
        offset=offset,
        lang=normalized_lang,
        include_undated=include_undated,
        include_origin_country=spec.case_law,
        include_implemented_by_country=include_implemented_by_country,
    )
    rows = parse_bindings(query_sparql(query))
    return spec, rows


def call_relation_result(
    *,
    method_name: str,
    celex: str,
    since: date | datetime | str | None,
    to: date | datetime | str | None,
    include_undated: bool,
    resource_type: str | None,
    limit: int,
    offset: int,
    lang: str,
    direction: str | None,
    validate_pagination: Callable[[int, int], None],
    normalize_lang: Callable[[str], str],
    normalize_resource_type: Callable[[str | None], str | None],
    normalize_direction: Callable[[str | None], str | None],
    normalize_date_bounds: Callable[
        [date | datetime | str | None, date | datetime | str | None],
        tuple[str | None, str | None],
    ],
    resolve_work_uri: Callable[[str], str],
    query_sparql: QueryFn,
    list_result_builder: ListResultBuilder,
) -> ListResult[RelationItem] | ListResult[CaseLawItem]:
    spec, rows = fetch_relation_rows(
        method_name=method_name,
        celex=celex,
        since=since,
        to=to,
        include_undated=include_undated,
        resource_type=resource_type,
        limit=limit,
        offset=offset,
        lang=lang,
        direction=direction,
        include_implemented_by_country=False,
        validate_pagination=validate_pagination,
        normalize_lang=normalize_lang,
        normalize_resource_type=normalize_resource_type,
        normalize_direction=normalize_direction,
        normalize_date_bounds=normalize_date_bounds,
        resolve_work_uri=resolve_work_uri,
        query_sparql=query_sparql,
    )

    if spec.case_law:
        case_items = parse_case_law_items(rows)
        return cast(
            ListResult[CaseLawItem],
            list_result_builder(
                query_name=method_name,
                items=case_items,
                limit=limit,
                offset=offset,
            ),
        )

    relation_items = parse_relation_items(rows)
    return cast(
        ListResult[RelationItem],
        list_result_builder(
            query_name=method_name,
            items=relation_items,
            limit=limit,
            offset=offset,
        ),
    )


def call_nim_result(
    *,
    method_name: str,
    celex: str,
    since: date | datetime | str | None,
    to: date | datetime | str | None,
    include_undated: bool,
    resource_type: str | None,
    limit: int,
    offset: int,
    lang: str,
    direction: str | None,
    validate_pagination: Callable[[int, int], None],
    normalize_lang: Callable[[str], str],
    normalize_resource_type: Callable[[str | None], str | None],
    normalize_direction: Callable[[str | None], str | None],
    normalize_date_bounds: Callable[
        [date | datetime | str | None, date | datetime | str | None],
        tuple[str | None, str | None],
    ],
    resolve_work_uri: Callable[[str], str],
    query_sparql: QueryFn,
    list_result_builder: ListResultBuilder,
) -> ListResult[NIMItem]:
    _, rows = fetch_relation_rows(
        method_name=method_name,
        celex=celex,
        since=since,
        to=to,
        include_undated=include_undated,
        resource_type=resource_type,
        limit=limit,
        offset=offset,
        lang=lang,
        direction=direction,
        include_implemented_by_country=True,
        validate_pagination=validate_pagination,
        normalize_lang=normalize_lang,
        normalize_resource_type=normalize_resource_type,
        normalize_direction=normalize_direction,
        normalize_date_bounds=normalize_date_bounds,
        resolve_work_uri=resolve_work_uri,
        query_sparql=query_sparql,
    )
    nim_items = parse_nim_items(rows)
    return cast(
        ListResult[NIMItem],
        list_result_builder(
            query_name=method_name,
            items=nim_items,
            limit=limit,
            offset=offset,
        ),
    )
