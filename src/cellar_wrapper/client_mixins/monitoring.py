"""Monitoring methods (`new_*`) for delta-style queries."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime

from cellar_wrapper.client_mixins.protocols import ClientOpsProtocol
from cellar_wrapper.constants import DEFAULT_LANGUAGE, DEFAULT_LIMIT, DEFAULT_OFFSET
from cellar_wrapper.errors import CellarValidationError
from cellar_wrapper.models import ActRef, CaseLawItem, ListResult, RelationItem


def _require_since(method_name: str, since: date | datetime | str | None) -> date | datetime | str:
    if since is None:
        raise CellarValidationError(f"{method_name} requires since")
    return since


def _call_monitor_relation(
    self: ClientOpsProtocol,
    *,
    method_name: str,
    celex: str,
    since: date | datetime | str,
    resource_type: str | None,
    limit: int,
    offset: int,
    lang: str,
) -> ListResult[RelationItem]:
    return self._call_relation_items(
        method_name=method_name,
        celex=celex,
        since=_require_since(method_name, since),
        resource_type=resource_type,
        limit=limit,
        offset=offset,
        lang=lang,
    )


def _call_monitor_case_law(
    self: ClientOpsProtocol,
    *,
    method_name: str,
    celex: str,
    since: date | datetime | str,
    resource_type: str | None,
    limit: int,
    offset: int,
    lang: str,
) -> ListResult[CaseLawItem]:
    return self._call_case_law_items(
        method_name=method_name,
        celex=celex,
        since=_require_since(method_name, since),
        resource_type=resource_type,
        limit=limit,
        offset=offset,
        lang=lang,
    )


class MonitoringMixin:
    """Methods for date-bounded discovery (`date > since`)."""

    def new_citations(
        self: ClientOpsProtocol,
        celex: str,
        since: date | datetime | str,
        *,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_monitor_relation(
            self,
            method_name="new_citations",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def new_amendments(
        self: ClientOpsProtocol,
        celex: str,
        since: date | datetime | str,
        *,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_monitor_relation(
            self,
            method_name="new_amendments",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def new_delegated_acts(
        self: ClientOpsProtocol,
        celex: str,
        since: date | datetime | str,
        *,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_monitor_relation(
            self,
            method_name="new_delegated_acts",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def new_case_law(
        self: ClientOpsProtocol,
        celex: str,
        since: date | datetime | str,
        *,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[CaseLawItem]:
        return _call_monitor_case_law(
            self,
            method_name="new_case_law",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def new_corrigenda(
        self: ClientOpsProtocol,
        celex: str,
        since: date | datetime | str,
        *,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_monitor_relation(
            self,
            method_name="new_corrigenda",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def new_consolidated(
        self: ClientOpsProtocol,
        celex: str,
        since: date | datetime | str,
        *,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_monitor_relation(
            self,
            method_name="new_consolidated",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def new_nims(
        self: ClientOpsProtocol,
        celex: str,
        since: date | datetime | str,
        *,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_monitor_relation(
            self,
            method_name="new_nims",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def new_by_eurovoc(
        self: ClientOpsProtocol,
        tags: Sequence[str],
        since: date | datetime | str,
        *,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[ActRef]:
        return self.search_by_eurovoc(
            tags,
            since=_require_since("new_by_eurovoc", since),
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )
