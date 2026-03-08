"""List/result builders shared by client mixins."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TypeVar

from cellar_wrapper.models import ListResult, QueryMeta

T = TypeVar("T")


def build_query_meta(
    query_name: str,
    *,
    endpoint: str,
    limit: int | None,
    offset: int | None,
) -> QueryMeta:
    return QueryMeta(
        query_name=query_name,
        endpoint=endpoint,
        executed_at=datetime.now(UTC),
        limit=limit,
        offset=offset,
    )


def build_list_result(
    *,
    query_name: str,
    items: list[T],
    endpoint: str,
    limit: int | None,
    offset: int | None,
) -> ListResult[T]:
    return ListResult[T](
        items=items,
        returned_count=len(items),
        meta=build_query_meta(query_name, endpoint=endpoint, limit=limit, offset=offset),
    )
