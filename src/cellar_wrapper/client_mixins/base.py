"""Base functionality shared by all CellarClient mixins."""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import UTC, date, datetime
from types import TracebackType
from typing import TypeVar, cast

from cellar_wrapper.constants import (
    DEFAULT_RESOURCE_BASE_URL,
    DEFAULT_RETRIES,
    DEFAULT_SPARQL_ENDPOINT,
    MAX_LIMIT,
)
from cellar_wrapper.errors import CellarValidationError
from cellar_wrapper.http import HttpTransport, TimeoutConfig
from cellar_wrapper.models import ActRef, CaseLawItem, ListResult, QueryMeta, RelationItem
from cellar_wrapper.parser import parse_bindings, parse_case_law_items, parse_relation_items
from cellar_wrapper.sparql import build_relation_query

from .relation_specs import RELATION_CALL_SPECS

CELEX_RE = re.compile(r"^[0-9A-Z()_\-]{5,40}$")
LANG_RE = re.compile(r"^[a-zA-Z]{3}$")
RESOURCE_TYPE_RE = re.compile(r"^[A-Z_]+$")

T = TypeVar("T")


class ClientBase:
    """Shared core implementation for the public client."""

    def __init__(
        self,
        *,
        base_url_sparql: str = DEFAULT_SPARQL_ENDPOINT,
        base_url_resource: str = DEFAULT_RESOURCE_BASE_URL,
        timeout: TimeoutConfig | None = None,
        retries: int = DEFAULT_RETRIES,
        user_agent: str = "cellar-wrapper/0.1.0",
        transport: HttpTransport | None = None,
    ) -> None:
        if retries < 1:
            raise CellarValidationError("retries must be >= 1")
        self._base_url_resource = base_url_resource.rstrip("/")
        self._transport = transport or HttpTransport(
            sparql_endpoint=base_url_sparql,
            retries=retries,
            user_agent=user_agent,
            timeout=timeout,
        )

    def close(self) -> None:
        """Close underlying HTTP resources."""
        self._transport.close()

    def __enter__(self) -> ClientBase:
        """Context-manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Context-manager exit."""
        self.close()

    def _normalize_celex(self, celex: str) -> str:
        normalized = celex.strip().upper()
        if not CELEX_RE.fullmatch(normalized):
            raise CellarValidationError(f"Invalid CELEX identifier: {celex!r}")
        return normalized

    def _normalize_lang(self, lang: str) -> str:
        normalized = lang.strip().lower()
        if not LANG_RE.fullmatch(normalized):
            raise CellarValidationError(f"Invalid language code: {lang!r}")
        return normalized

    def _normalize_resource_type(self, resource_type: str | None) -> str | None:
        if resource_type is None:
            return None
        normalized = resource_type.strip().upper()
        if not RESOURCE_TYPE_RE.fullmatch(normalized):
            raise CellarValidationError(f"Invalid resource_type: {resource_type!r}")
        return normalized

    def _coerce_since(self, since: date | datetime | str | None) -> str | None:
        if since is None:
            return None
        if isinstance(since, datetime):
            return since.isoformat()
        if isinstance(since, date):
            return since.isoformat()

        candidate = since.strip()
        candidate_for_parse = candidate.replace("Z", "+00:00")
        try:
            datetime.fromisoformat(candidate_for_parse)
            return candidate
        except ValueError:
            pass

        try:
            date.fromisoformat(candidate)
            return candidate
        except ValueError as exc:
            raise CellarValidationError(
                f"Invalid since value (expected ISO date/datetime): {since!r}"
            ) from exc

    @staticmethod
    def _validate_pagination(limit: int, offset: int) -> None:
        if limit <= 0:
            raise CellarValidationError("limit must be > 0")
        if limit > MAX_LIMIT:
            raise CellarValidationError(f"limit cannot exceed {MAX_LIMIT}")
        if offset < 0:
            raise CellarValidationError("offset cannot be negative")

    def _meta(self, query_name: str, *, limit: int | None, offset: int | None) -> QueryMeta:
        return QueryMeta(
            query_name=query_name,
            endpoint=self._transport.sparql_endpoint,
            executed_at=datetime.now(UTC),
            limit=limit,
            offset=offset,
        )

    def _list_result(
        self,
        *,
        query_name: str,
        items: list[T],
        limit: int | None,
        offset: int | None,
    ) -> ListResult[T]:
        return ListResult[T](
            items=items,
            returned_count=len(items),
            meta=self._meta(query_name, limit=limit, offset=offset),
        )

    def _run_list_query(
        self,
        *,
        query_name: str,
        query: str,
        parser: Callable[[list[dict[str, dict[str, str]]]], list[T]],
        limit: int | None,
        offset: int | None,
    ) -> ListResult[T]:
        rows = parse_bindings(self._transport.query_sparql(query))
        items = parser(rows)
        return self._list_result(
            query_name=query_name,
            items=items,
            limit=limit,
            offset=offset,
        )

    def _resolve_work_uri(self, celex: str) -> str:
        return self.resolve_celex(celex).uri

    def resolve_celex(self, celex: str) -> ActRef:  # pragma: no cover - implemented in LookupMixin
        raise NotImplementedError

    def _call_relation(
        self,
        *,
        method_name: str,
        celex: str,
        since: date | datetime | str | None,
        resource_type: str | None,
        limit: int,
        offset: int,
        lang: str,
    ) -> ListResult[RelationItem] | ListResult[CaseLawItem]:
        spec = RELATION_CALL_SPECS.get(method_name)
        if spec is None:
            raise CellarValidationError(f"Unsupported relation method: {method_name}")
        self._validate_pagination(limit, offset)
        normalized_lang = self._normalize_lang(lang)
        normalized_type = self._normalize_resource_type(resource_type) or spec.default_resource_type
        since_value = self._coerce_since(since)
        work_uri = self._resolve_work_uri(celex)

        query = build_relation_query(
            work_uri,
            predicates=spec.predicates,
            direction=spec.direction,
            since=since_value,
            resource_type=normalized_type,
            limit=limit,
            offset=offset,
            lang=normalized_lang,
        )
        rows = parse_bindings(self._transport.query_sparql(query))

        if spec.case_law:
            case_items = parse_case_law_items(rows)
            return self._list_result(
                query_name=method_name,
                items=case_items,
                limit=limit,
                offset=offset,
            )

        relation_items = parse_relation_items(rows)
        return self._list_result(
            query_name=method_name,
            items=relation_items,
            limit=limit,
            offset=offset,
        )

    def _call_relation_items(
        self,
        *,
        method_name: str,
        celex: str,
        since: date | datetime | str | None,
        resource_type: str | None,
        limit: int,
        offset: int,
        lang: str,
    ) -> ListResult[RelationItem]:
        result = self._call_relation(
            method_name=method_name,
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )
        return cast(ListResult[RelationItem], result)

    def _call_case_law_items(
        self,
        *,
        method_name: str,
        celex: str,
        since: date | datetime | str | None,
        resource_type: str | None,
        limit: int,
        offset: int,
        lang: str,
    ) -> ListResult[CaseLawItem]:
        result = self._call_relation(
            method_name=method_name,
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )
        return cast(ListResult[CaseLawItem], result)
