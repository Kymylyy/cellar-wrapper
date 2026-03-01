"""Search-related client methods."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime

from cellar_wrapper.client_mixins.protocols import ClientOpsProtocol
from cellar_wrapper.constants import DEFAULT_LANGUAGE, DEFAULT_LIMIT, DEFAULT_OFFSET, MAX_LIMIT
from cellar_wrapper.errors import CellarValidationError
from cellar_wrapper.models import ActRef, EurovocTag, ListResult
from cellar_wrapper.parser import parse_act_refs, parse_eurovoc_tags
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
        normalized_tags = [tag.strip() for tag in tags if tag.strip()]
        if not normalized_tags:
            raise CellarValidationError("tags cannot be empty")
        concept_uris: list[str] = []
        seen_concepts: set[str] = set()
        for tag in normalized_tags:
            concept_offset = 0
            while True:
                concept_page = self.find_eurovoc_concept(tag, limit=MAX_LIMIT, offset=concept_offset)
                for concept in concept_page.items:
                    if concept.concept_uri in seen_concepts:
                        continue
                    seen_concepts.add(concept.concept_uri)
                    concept_uris.append(concept.concept_uri)
                if concept_page.returned_count < MAX_LIMIT:
                    break
                concept_offset += MAX_LIMIT
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

        query = build_find_eurovoc_concept_query(label, limit=limit, offset=offset)
        return self._run_list_query(
            query_name="find_eurovoc_concept",
            query=query,
            parser=parse_eurovoc_tags,
            limit=limit,
            offset=offset,
        )
