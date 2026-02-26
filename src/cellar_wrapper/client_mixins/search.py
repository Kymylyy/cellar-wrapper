"""Search-related client methods."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime

from cellar_wrapper.client_mixins.protocols import ClientOpsProtocol
from cellar_wrapper.constants import DEFAULT_LANGUAGE, DEFAULT_LIMIT, DEFAULT_OFFSET
from cellar_wrapper.errors import CellarValidationError
from cellar_wrapper.models import ActRef, EurovocTag, ListResult
from cellar_wrapper.parser import parse_act_refs, parse_bindings, parse_eurovoc_tags
from cellar_wrapper.sparql import (
    build_find_eurovoc_concept_query,
    build_search_by_eurovoc_query,
    build_search_by_subject_matter_query,
    build_search_by_title_query,
    build_search_communications_query,
)


class SearchMixin:
    """Methods for thematic/title queries."""

    def search_by_eurovoc(
        self: ClientOpsProtocol,
        tags: Sequence[str],
        *,
        resource_type: str | None = None,
        since: date | datetime | str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[ActRef]:
        self._validate_pagination(limit, offset)
        query = build_search_by_eurovoc_query(
            list(tags),
            resource_type=self._normalize_resource_type(resource_type),
            since=self._coerce_since(since),
            limit=limit,
            offset=offset,
            lang=self._normalize_lang(lang),
        )
        rows = parse_bindings(self._transport.query_sparql(query))
        return self._list_result(
            query_name="search_by_eurovoc",
            items=parse_act_refs(rows),
            limit=limit,
            offset=offset,
        )

    def search_by_subject_matter(
        self: ClientOpsProtocol,
        codes: Sequence[str],
        *,
        resource_type: str | None = None,
        since: date | datetime | str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[ActRef]:
        self._validate_pagination(limit, offset)
        query = build_search_by_subject_matter_query(
            list(codes),
            resource_type=self._normalize_resource_type(resource_type),
            since=self._coerce_since(since),
            limit=limit,
            offset=offset,
            lang=self._normalize_lang(lang),
        )
        rows = parse_bindings(self._transport.query_sparql(query))
        return self._list_result(
            query_name="search_by_subject_matter",
            items=parse_act_refs(rows),
            limit=limit,
            offset=offset,
        )

    def search_by_title(
        self: ClientOpsProtocol,
        keyword: str,
        *,
        resource_type: str | None = None,
        since: date | datetime | str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[ActRef]:
        self._validate_pagination(limit, offset)
        if not keyword.strip():
            raise CellarValidationError("keyword cannot be empty")
        query = build_search_by_title_query(
            keyword,
            resource_type=self._normalize_resource_type(resource_type),
            since=self._coerce_since(since),
            limit=limit,
            offset=offset,
            lang=self._normalize_lang(lang),
        )
        rows = parse_bindings(self._transport.query_sparql(query))
        return self._list_result(
            query_name="search_by_title",
            items=parse_act_refs(rows),
            limit=limit,
            offset=offset,
        )

    def search_communications(
        self: ClientOpsProtocol,
        dg: str,
        *,
        since: date | datetime | str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[ActRef]:
        if not dg.strip():
            raise CellarValidationError("dg cannot be empty")
        self._validate_pagination(limit, offset)
        query = build_search_communications_query(
            dg,
            since=self._coerce_since(since),
            limit=limit,
            offset=offset,
            lang=self._normalize_lang(lang),
        )
        rows = parse_bindings(self._transport.query_sparql(query))
        return self._list_result(
            query_name="search_communications",
            items=parse_act_refs(rows),
            limit=limit,
            offset=offset,
        )

    def find_eurovoc_concept(
        self: ClientOpsProtocol,
        label: str,
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
    ) -> ListResult[EurovocTag]:
        self._validate_pagination(limit, offset)
        if not label.strip():
            raise CellarValidationError("label cannot be empty")

        query = build_find_eurovoc_concept_query(label, limit=limit, offset=offset)
        rows = parse_bindings(self._transport.query_sparql(query))
        return self._list_result(
            query_name="find_eurovoc_concept",
            items=parse_eurovoc_tags(rows),
            limit=limit,
            offset=offset,
        )
