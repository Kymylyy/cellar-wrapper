"""Typing protocols shared by client mixins."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime
from typing import Any, Protocol, TypeVar

from cellar_wrapper.models import ActRef, CaseLawItem, ListResult, RelationItem

T = TypeVar("T")


class TransportProtocol(Protocol):
    """Minimal transport contract required by mixins."""

    sparql_endpoint: str

    def query_sparql(self, query: str) -> dict[str, Any]: ...

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

    def _normalize_resource_type(self, resource_type: str | None) -> str | None: ...

    def _coerce_since(self, since: date | datetime | str | None) -> str | None: ...

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
    ) -> ListResult[T]: ...

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
    ) -> ListResult[RelationItem]: ...

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
    ) -> ListResult[CaseLawItem]: ...

    def search_by_eurovoc(
        self,
        tags: Sequence[str],
        *,
        resource_type: str | None = None,
        since: date | datetime | str | None = None,
        limit: int,
        offset: int,
        lang: str,
    ) -> ListResult[ActRef]: ...

    def resolve_celex(self, celex: str) -> ActRef: ...
