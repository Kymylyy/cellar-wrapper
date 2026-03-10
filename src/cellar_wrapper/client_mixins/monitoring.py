"""Monitoring methods (`new_*`) for delta-style queries."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime

from cellar_wrapper.client_mixins.protocols import ClientOpsProtocol
from cellar_wrapper.constants import DEFAULT_LANGUAGE, DEFAULT_LIMIT, DEFAULT_OFFSET
from cellar_wrapper.errors import CellarValidationError
from cellar_wrapper.models import ActRef, CaseLawItem, ListResult, NIMItem, RelationItem
from cellar_wrapper.parser import parse_act_refs
from cellar_wrapper.sparql import build_search_by_eurovoc_query


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
        include_undated=False,
        resource_type=resource_type,
        limit=limit,
        offset=offset,
        lang=lang,
        direction=None,
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
        include_undated=False,
        resource_type=resource_type,
        limit=limit,
        offset=offset,
        lang=lang,
    )


def _call_monitor_nims(
    self: ClientOpsProtocol,
    *,
    method_name: str,
    celex: str,
    since: date | datetime | str,
    resource_type: str | None,
    limit: int,
    offset: int,
    lang: str,
) -> ListResult[NIMItem]:
    return self._call_nim_items(
        method_name=method_name,
        celex=celex,
        since=_require_since(method_name, since),
        include_undated=False,
        resource_type=resource_type,
        limit=limit,
        offset=offset,
        lang=lang,
    )


class MonitoringMixin:
    """Methods for date-bounded discovery (`date > since`)."""

    def _new_relation(
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
        return _call_monitor_relation(
            self,
            method_name=method_name,
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def _new_case_law(
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
        return _call_monitor_case_law(
            self,
            method_name=method_name,
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def _new_nims(
        self: ClientOpsProtocol,
        *,
        method_name: str,
        celex: str,
        since: date | datetime | str,
        resource_type: str | None,
        limit: int,
        offset: int,
        lang: str,
    ) -> ListResult[NIMItem]:
        return _call_monitor_nims(
            self,
            method_name=method_name,
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

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
        return self._new_relation(
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
        return self._new_relation(
            method_name="new_amendments",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def new_repeals(
        self: ClientOpsProtocol,
        celex: str,
        since: date | datetime | str,
        *,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return self._new_relation(
            method_name="new_repeals",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def new_proposals_to_amend(
        self: ClientOpsProtocol,
        celex: str,
        since: date | datetime | str,
        *,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return self._new_relation(
            method_name="new_proposals_to_amend",
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
        return self._new_relation(
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
        return self._new_case_law(
            method_name="new_case_law",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def new_preliminary_questions(
        self: ClientOpsProtocol,
        celex: str,
        since: date | datetime | str,
        *,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[CaseLawItem]:
        return self._new_case_law(
            method_name="new_preliminary_questions",
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
        return self._new_relation(
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
        return self._new_relation(
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
    ) -> ListResult[NIMItem]:
        return self._new_nims(
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
        self._validate_pagination(limit, offset)
        normalized_tags = self._normalize_non_empty_tags(tags)
        concept_uris = self._resolve_eurovoc_concept_uris(normalized_tags)
        if not concept_uris:
            return self._list_result(
                query_name="new_by_eurovoc",
                items=[],
                limit=limit,
                offset=offset,
            )
        since_value = self._coerce_since(_require_since("new_by_eurovoc", since))
        query = build_search_by_eurovoc_query(
            concept_uris,
            resource_type=self._normalize_resource_type(resource_type),
            since=since_value,
            limit=limit,
            offset=offset,
            lang=self._normalize_lang(lang),
            include_undated=False,
        )
        return self._run_list_query(
            query_name="new_by_eurovoc",
            query=query,
            parser=parse_act_refs,
            limit=limit,
            offset=offset,
        )
