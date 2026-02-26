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
        return self._call_relation_items(
            method_name="new_citations",
            celex=celex,
            since=_require_since("new_citations", since),
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
        return self._call_relation_items(
            method_name="new_amendments",
            celex=celex,
            since=_require_since("new_amendments", since),
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
        return self._call_relation_items(
            method_name="new_delegated_acts",
            celex=celex,
            since=_require_since("new_delegated_acts", since),
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
        return self._call_case_law_items(
            method_name="new_case_law",
            celex=celex,
            since=_require_since("new_case_law", since),
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
        return self._call_relation_items(
            method_name="new_corrigenda",
            celex=celex,
            since=_require_since("new_corrigenda", since),
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
        return self._call_relation_items(
            method_name="new_consolidated",
            celex=celex,
            since=_require_since("new_consolidated", since),
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
        return self._call_relation_items(
            method_name="new_nims",
            celex=celex,
            since=_require_since("new_nims", since),
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
