"""Search-related client methods."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime

from cellar_wrapper.client_mixins.protocols import ClientOpsProtocol
from cellar_wrapper.constants import DEFAULT_LANGUAGE, DEFAULT_LIMIT, DEFAULT_OFFSET
from cellar_wrapper.errors import CellarValidationError
from cellar_wrapper.eurovoc_index import LOCAL_EUROVOC_ENDPOINT
from cellar_wrapper.models import ActRef, EurovocTag, ListResult
from cellar_wrapper.parser import parse_act_refs
from cellar_wrapper.sparql import (
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
        normalized_tags = self._normalize_non_empty_tags(tags)
        concept_uris = self._resolve_eurovoc_concept_uris(normalized_tags)
        if not concept_uris:
            return self._list_result(
                query_name="search_by_eurovoc",
                items=[],
                limit=limit,
                offset=offset,
            )
        query = build_search_by_eurovoc_query(
            concept_uris,
            resource_type=self._normalize_resource_type(resource_type),
            since=self._coerce_since(since),
            limit=limit,
            offset=offset,
            lang=self._normalize_lang(lang),
            include_undated=True,
        )
        return self._run_list_query(
            query_name="search_by_eurovoc",
            query=query,
            parser=parse_act_refs,
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
        normalized_codes = [code.strip() for code in codes if code.strip()]
        if not normalized_codes:
            raise CellarValidationError("codes cannot be empty")
        query = build_search_by_subject_matter_query(
            normalized_codes,
            resource_type=self._normalize_resource_type(resource_type),
            since=self._coerce_since(since),
            limit=limit,
            offset=offset,
            lang=self._normalize_lang(lang),
        )
        return self._run_list_query(
            query_name="search_by_subject_matter",
            query=query,
            parser=parse_act_refs,
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
        return self._run_list_query(
            query_name="search_by_title",
            query=query,
            parser=parse_act_refs,
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
        return self._run_list_query(
            query_name="search_communications",
            query=query,
            parser=parse_act_refs,
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
        items = self._find_local_eurovoc_concepts(label, limit=limit, offset=offset)
        return self._list_result(
            query_name="find_eurovoc_concept",
            items=items,
            limit=limit,
            offset=offset,
            endpoint=LOCAL_EUROVOC_ENDPOINT,
        )
