"""Case-law specific client methods."""

from __future__ import annotations

from datetime import date, datetime

from cellar_wrapper.client_mixins.protocols import ClientOpsProtocol
from cellar_wrapper.constants import DEFAULT_LANGUAGE, DEFAULT_LIMIT, DEFAULT_OFFSET
from cellar_wrapper.models import CaseLawItem, ListResult, RelationItem
from cellar_wrapper.parser import parse_bindings, parse_case_law_items, parse_relation_items
from cellar_wrapper.sparql import (
    build_ag_opinions_query,
    build_article_annotations_query,
    build_national_decisions_query,
)


class CaseLawMixin:
    """Methods for CJEU and national case-law."""

    def get_cjeu_judgments(
        self: ClientOpsProtocol,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[CaseLawItem]:
        return self._call_case_law_items(
            method_name="get_cjeu_judgments",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def get_ag_opinions(
        self: ClientOpsProtocol,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        self._validate_pagination(limit, offset)
        query = build_ag_opinions_query(
            self._resolve_work_uri(celex),
            since=self._coerce_since(since),
            limit=limit,
            offset=offset,
            lang=self._normalize_lang(lang),
        )
        rows = parse_bindings(self._transport.query_sparql(query))
        return self._list_result(
            query_name="get_ag_opinions",
            items=parse_relation_items(rows),
            limit=limit,
            offset=offset,
        )

    def get_preliminary_questions(
        self: ClientOpsProtocol,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[CaseLawItem]:
        return self._call_case_law_items(
            method_name="get_preliminary_questions",
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def get_national_decisions(
        self: ClientOpsProtocol,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[CaseLawItem]:
        self._validate_pagination(limit, offset)
        query = build_national_decisions_query(
            self._normalize_celex(celex),
            since=self._coerce_since(since),
            limit=limit,
            offset=offset,
            lang=self._normalize_lang(lang),
        )
        rows = parse_bindings(self._transport.query_sparql(query))
        return self._list_result(
            query_name="get_national_decisions",
            items=parse_case_law_items(rows),
            limit=limit,
            offset=offset,
        )

    def get_article_annotations(
        self: ClientOpsProtocol,
        celex: str,
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
    ) -> ListResult[RelationItem]:
        self._validate_pagination(limit, offset)
        query = build_article_annotations_query(self._resolve_work_uri(celex), limit=limit, offset=offset)
        rows = parse_bindings(self._transport.query_sparql(query))
        return self._list_result(
            query_name="get_article_annotations",
            items=parse_relation_items(rows),
            limit=limit,
            offset=offset,
        )
