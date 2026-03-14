"""Typing protocols shared by client mixins."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import date, datetime
from typing import Any, Protocol, TypeVar

from cellar_wrapper.models import ActRef, CaseLawItem, EurovocTag, ListResult, NIMItem, RelationItem

T = TypeVar("T")


class TransportProtocol(Protocol):
    """Minimal transport contract required by mixins."""

    @property
    def sparql_endpoint(self) -> str: ...

    def query_sparql(self, query: str) -> dict[str, Any]: ...

    def close(self) -> None: ...

    def download(
        self,
        url: str,
        *,
        accept: str,
        language: str | None = None,
    ) -> tuple[bytes, str, str]: ...


class ClientOpsProtocol(Protocol):
    """Shared client capabilities used by mixin methods."""

    _transport: TransportProtocol
    _base_url_resource: str

    def _normalize_celex(self, celex: str) -> str: ...

    def _normalize_lang(self, lang: str) -> str: ...

    def _normalize_resource_types(self, resource_types: Sequence[str] | None) -> list[str] | None: ...

    def _normalize_direction(self, direction: str | None) -> str | None: ...

    def _normalize_country(self, country: str | None) -> str | None: ...

    def _coerce_since(self, since: date | datetime | str | None) -> str | None: ...

    def _coerce_to(self, to: date | datetime | str | None) -> str | None: ...

    def _normalize_date_bounds(
        self,
        since: date | datetime | str | None,
        to: date | datetime | str | None,
    ) -> tuple[str | None, str | None]: ...

    @staticmethod
    def _validate_pagination(limit: int, offset: int) -> None: ...

    def _resolve_work_uri(self, celex: str) -> str: ...

    def _list_result(
        self,
        *,
        query_name: str,
        items: list[T],
        limit: int | None,
        offset: int | None,
        endpoint: str | None = None,
    ) -> ListResult[T]: ...

    def _run_list_query(
        self,
        *,
        query_name: str,
        query: str,
        parser: Callable[[list[dict[str, dict[str, str]]]], list[T]],
        limit: int | None,
        offset: int | None,
    ) -> ListResult[T]: ...

    def _find_local_eurovoc_concepts(
        self,
        label: str,
        *,
        limit: int,
        offset: int,
    ) -> list[EurovocTag]: ...

    def _normalize_non_empty_tags(self, tags: Sequence[str], *, field_name: str = "tags") -> list[str]: ...

    def _resolve_eurovoc_concept_uris(self, tags: Sequence[str]) -> list[str]: ...

    def _resolve_subject_matter_concept_uris(self, codes: Sequence[str]) -> list[str]: ...

    def _call_relation_items(
        self,
        *,
        method_name: str,
        celex: str,
        since: date | datetime | str | None,
        to: date | datetime | str | None,
        include_undated: bool,
        resource_types: Sequence[str] | None,
        limit: int,
        offset: int,
        lang: str,
        direction: str | None,
    ) -> ListResult[RelationItem]: ...

    def _call_case_law_items(
        self,
        *,
        method_name: str,
        celex: str,
        since: date | datetime | str | None,
        to: date | datetime | str | None,
        include_undated: bool,
        resource_types: Sequence[str] | None,
        limit: int,
        offset: int,
        lang: str,
    ) -> ListResult[CaseLawItem]: ...

    def _call_nim_items(
        self,
        *,
        method_name: str,
        celex: str,
        since: date | datetime | str | None,
        to: date | datetime | str | None,
        include_undated: bool,
        resource_types: Sequence[str] | None,
        limit: int,
        offset: int,
        lang: str,
    ) -> ListResult[NIMItem]: ...

    def _new_relation(
        self,
        *,
        method_name: str,
        celex: str,
        since: date | datetime | str,
        to: date | datetime | str | None,
        resource_types: Sequence[str] | None,
        limit: int,
        offset: int,
        lang: str,
    ) -> ListResult[RelationItem]: ...

    def _new_case_law(
        self,
        *,
        method_name: str,
        celex: str,
        since: date | datetime | str,
        to: date | datetime | str | None,
        resource_types: Sequence[str] | None,
        limit: int,
        offset: int,
        lang: str,
    ) -> ListResult[CaseLawItem]: ...

    def _new_nims(
        self,
        *,
        method_name: str,
        celex: str,
        since: date | datetime | str,
        to: date | datetime | str | None,
        resource_types: Sequence[str] | None,
        limit: int,
        offset: int,
        lang: str,
    ) -> ListResult[NIMItem]: ...

    def search_by_eurovoc(
        self,
        tags: Sequence[str],
        *,
        resource_types: Sequence[str] | None = None,
        since: date | datetime | str | None = None,
        to: date | datetime | str | None = None,
        limit: int,
        offset: int,
        lang: str,
    ) -> ListResult[ActRef]: ...

    def find_eurovoc_concept(
        self,
        label: str,
        *,
        limit: int,
        offset: int,
    ) -> ListResult[EurovocTag]: ...

    def resolve_celex(self, celex: str) -> ActRef: ...
