"""Relation-oriented client methods."""

from __future__ import annotations

from datetime import date, datetime

from cellar_wrapper.client_mixins.protocols import ClientOpsProtocol
from cellar_wrapper.constants import DEFAULT_LANGUAGE, DEFAULT_LIMIT, DEFAULT_OFFSET
from cellar_wrapper.models import ListResult, RelationItem


def _call_relation(
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


class RelationsMixin:
    """Methods for legal relation traversals."""

    def get_amendments(
        self: ClientOpsProtocol,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_relation(
            self,
            method_name="get_amendments",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def get_repeals(
        self: ClientOpsProtocol,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_relation(
            self,
            method_name="get_repeals",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def get_citations(
        self: ClientOpsProtocol,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_relation(
            self,
            method_name="get_citations",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def get_delegated_acts(
        self: ClientOpsProtocol,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_relation(
            self,
            method_name="get_delegated_acts",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def get_completing_acts(
        self: ClientOpsProtocol,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_relation(
            self,
            method_name="get_completing_acts",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def get_proposals_to_amend(
        self: ClientOpsProtocol,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_relation(
            self,
            method_name="get_proposals_to_amend",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def get_adopted_act(
        self: ClientOpsProtocol,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_relation(
            self,
            method_name="get_adopted_act",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def get_related_works(
        self: ClientOpsProtocol,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_relation(
            self,
            method_name="get_related_works",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def get_other_relations(
        self: ClientOpsProtocol,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return _call_relation(
            self,
            method_name="get_other_relations",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )
