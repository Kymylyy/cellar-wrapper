"""Lifecycle methods for consolidations, corrigenda, dossier and deadlines."""

from __future__ import annotations

from datetime import date, datetime

from cellar_wrapper.client_mixins.protocols import ClientOpsProtocol
from cellar_wrapper.constants import DEFAULT_LANGUAGE, DEFAULT_LIMIT, DEFAULT_OFFSET
from cellar_wrapper.models import ListResult, RelationItem
from cellar_wrapper.parser import parse_relation_items
from cellar_wrapper.sparql import build_deadlines_query, build_dossier_query


def _call_lifecycle_relation(
    self: ClientOpsProtocol,
    *,
    method_name: str,
    celex: str,
    since: date | datetime | str | None,
    resource_type: str | None,
    limit: int,
    offset: int,
    lang: str,
) -> ListResult[RelationItem]:
    return self._call_relation_items(
        method_name=method_name,
        celex=celex,
        since=since,
        include_undated=True,
        resource_type=resource_type,
        limit=limit,
        offset=offset,
        lang=lang,
    )


class LifecycleMixin:
    """Methods covering act lifecycle and procedure."""

    def get_consolidated_versions(
        self: ClientOpsProtocol,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_lifecycle_relation(
            self,
            method_name="get_consolidated_versions",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def get_corrigenda(
        self: ClientOpsProtocol,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_lifecycle_relation(
            self,
            method_name="get_corrigenda",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def get_nims(
        self: ClientOpsProtocol,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_lifecycle_relation(
            self,
            method_name="get_nims",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def get_dossier(
        self: ClientOpsProtocol,
        celex: str,
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        self._validate_pagination(limit, offset)
        query = build_dossier_query(
            self._resolve_work_uri(celex),
            limit=limit,
            offset=offset,
            lang=self._normalize_lang(lang),
        )
        return self._run_list_query(
            query_name="get_dossier",
            query=query,
            parser=parse_relation_items,
            limit=limit,
            offset=offset,
        )

    def get_opinions(
        self: ClientOpsProtocol,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_lifecycle_relation(
            self,
            method_name="get_opinions",
            celex=celex,
            since=since,
            resource_type=None,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def get_deadlines(
        self: ClientOpsProtocol,
        celex: str,
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
    ) -> ListResult[RelationItem]:
        self._validate_pagination(limit, offset)
        query = build_deadlines_query(self._resolve_work_uri(celex), limit=limit, offset=offset)
        return self._run_list_query(
            query_name="get_deadlines",
            query=query,
            parser=parse_relation_items,
            limit=limit,
            offset=offset,
        )
