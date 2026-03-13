"""Base functionality shared by all CellarClient mixins."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import date, datetime
from types import TracebackType
from typing import TypeVar, cast

from cellar_wrapper.constants import (
    DEFAULT_MAX_DOWNLOAD_BYTES,
    DEFAULT_RESOURCE_BASE_URL,
    DEFAULT_RETRIES,
    DEFAULT_SPARQL_ENDPOINT,
    DEFAULT_USER_AGENT,
)
from cellar_wrapper.errors import CellarValidationError
from cellar_wrapper.eurovoc_index import load_default_eurovoc_index
from cellar_wrapper.http import HttpTransport, TimeoutConfig, validate_http_url
from cellar_wrapper.models import (
    ActRef,
    CaseLawItem,
    EurovocTag,
    ListResult,
    NIMItem,
    QueryMeta,
    RelationItem,
)
from cellar_wrapper.parser import parse_bindings
from cellar_wrapper.subject_matter_index import load_default_subject_matter_index

from .protocols import TransportProtocol
from .relation_execution import call_nim_result, call_relation_result, fetch_relation_rows
from .relation_specs import RelationCallSpec
from .result_builders import build_list_result, build_query_meta
from .validation import (
    coerce_date_bound,
    coerce_since,
    coerce_to,
    dedupe_non_empty_casefold,
    normalize_celex,
    normalize_country,
    normalize_direction,
    normalize_lang,
    normalize_non_empty_values,
    normalize_resource_type,
    validate_date_range,
    validate_pagination,
)

T = TypeVar("T")


class ClientBase:
    """Shared core implementation for the public client."""

    _transport: TransportProtocol
    _base_url_resource: str

    def __init__(
        self,
        *,
        base_url_sparql: str = DEFAULT_SPARQL_ENDPOINT,
        base_url_resource: str = DEFAULT_RESOURCE_BASE_URL,
        timeout: TimeoutConfig | None = None,
        retries: int = DEFAULT_RETRIES,
        max_download_bytes: int = DEFAULT_MAX_DOWNLOAD_BYTES,
        user_agent: str = DEFAULT_USER_AGENT,
        transport: TransportProtocol | None = None,
    ) -> None:
        if retries < 1:
            raise CellarValidationError("retries must be >= 1")
        if max_download_bytes < 1:
            raise CellarValidationError("max_download_bytes must be >= 1")
        normalized_sparql_endpoint = validate_http_url(base_url_sparql, field="base_url_sparql")
        normalized_resource_base = validate_http_url(base_url_resource, field="base_url_resource")
        self._base_url_resource = normalized_resource_base.rstrip("/")
        if transport is None:
            self._transport = HttpTransport(
                sparql_endpoint=normalized_sparql_endpoint,
                retries=retries,
                max_download_bytes=max_download_bytes,
                user_agent=user_agent,
                timeout=timeout,
            )
        else:
            self._transport = transport

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
        return normalize_celex(celex)

    def _normalize_lang(self, lang: str) -> str:
        return normalize_lang(lang)

    def _normalize_resource_type(self, resource_type: str | None) -> str | None:
        return normalize_resource_type(resource_type)

    def _normalize_direction(self, direction: str | None) -> str | None:
        return normalize_direction(direction)

    def _normalize_country(self, country: str | None) -> str | None:
        return normalize_country(country)

    def _coerce_since(self, since: date | datetime | str | None) -> str | None:
        return coerce_since(since)

    def _coerce_to(self, to: date | datetime | str | None) -> str | None:
        return coerce_to(to)

    def _normalize_date_bounds(
        self,
        since: date | datetime | str | None,
        to: date | datetime | str | None,
    ) -> tuple[str | None, str | None]:
        since_value = coerce_date_bound(since, field_name="since")
        to_value = coerce_date_bound(to, field_name="to")
        validate_date_range(since_value, to_value)
        return since_value, to_value

    @staticmethod
    def _validate_pagination(limit: int, offset: int) -> None:
        validate_pagination(limit, offset)

    def _meta(
        self,
        query_name: str,
        *,
        limit: int | None,
        offset: int | None,
        endpoint: str | None = None,
    ) -> QueryMeta:
        return build_query_meta(
            query_name,
            endpoint=endpoint or self._transport.sparql_endpoint,
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
        endpoint: str | None = None,
    ) -> ListResult[T]:
        return build_list_result(
            query_name=query_name,
            items=items,
            endpoint=endpoint or self._transport.sparql_endpoint,
            limit=limit,
            offset=offset,
        )

    def _find_local_eurovoc_concepts(
        self,
        label: str,
        *,
        limit: int,
        offset: int,
    ) -> list[EurovocTag]:
        index = load_default_eurovoc_index()
        return index.find_by_label(label, limit=limit, offset=offset)

    def _normalize_non_empty_tags(self, tags: Sequence[str], *, field_name: str = "tags") -> list[str]:
        return normalize_non_empty_values(tags, field_name=field_name)

    def _resolve_eurovoc_concept_uris(self, tags: Sequence[str]) -> list[str]:
        unique_tags = dedupe_non_empty_casefold(tags)
        index = load_default_eurovoc_index()
        return index.resolve_concept_uris(unique_tags)

    def _resolve_subject_matter_concept_uris(self, codes: Sequence[str]) -> list[str]:
        unique_codes = dedupe_non_empty_casefold(codes)
        index = load_default_subject_matter_index()
        return index.resolve_concept_uris(unique_codes)

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
        to: date | datetime | str | None,
        include_undated: bool,
        resource_type: str | None,
        limit: int,
        offset: int,
        lang: str,
        direction: str | None,
    ) -> ListResult[RelationItem] | ListResult[CaseLawItem]:
        return call_relation_result(
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
            validate_pagination=self._validate_pagination,
            normalize_lang=self._normalize_lang,
            normalize_resource_type=self._normalize_resource_type,
            normalize_direction=self._normalize_direction,
            normalize_date_bounds=self._normalize_date_bounds,
            resolve_work_uri=self._resolve_work_uri,
            query_sparql=self._transport.query_sparql,
            list_result_builder=self._list_result,
        )

    def _fetch_relation_rows(
        self,
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
    ) -> tuple[RelationCallSpec, list[dict[str, dict[str, str]]]]:
        return fetch_relation_rows(
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
            include_implemented_by_country=include_implemented_by_country,
            validate_pagination=self._validate_pagination,
            normalize_lang=self._normalize_lang,
            normalize_resource_type=self._normalize_resource_type,
            normalize_direction=self._normalize_direction,
            normalize_date_bounds=self._normalize_date_bounds,
            resolve_work_uri=self._resolve_work_uri,
            query_sparql=self._transport.query_sparql,
        )

    def _call_relation_items(
        self,
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
        direction: str | None = None,
    ) -> ListResult[RelationItem]:
        result = self._call_relation(
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
        )
        return cast(ListResult[RelationItem], result)

    def _call_case_law_items(
        self,
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
    ) -> ListResult[CaseLawItem]:
        result = self._call_relation(
            method_name=method_name,
            celex=celex,
            since=since,
            to=to,
            include_undated=include_undated,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
            direction=None,
        )
        return cast(ListResult[CaseLawItem], result)

    def _call_nim_items(
        self,
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
    ) -> ListResult[NIMItem]:
        return call_nim_result(
            method_name=method_name,
            celex=celex,
            since=since,
            to=to,
            include_undated=include_undated,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
            direction=None,
            validate_pagination=self._validate_pagination,
            normalize_celex=self._normalize_celex,
            normalize_lang=self._normalize_lang,
            normalize_resource_type=self._normalize_resource_type,
            normalize_direction=self._normalize_direction,
            normalize_date_bounds=self._normalize_date_bounds,
            resolve_work_uri=self._resolve_work_uri,
            query_sparql=self._transport.query_sparql,
            list_result_builder=self._list_result,
        )
