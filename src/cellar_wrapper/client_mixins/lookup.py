"""Lookup-related client methods."""

from __future__ import annotations

from cellar_wrapper.client_mixins.protocols import ClientOpsProtocol
from cellar_wrapper.constants import DEFAULT_LANGUAGE, DEFAULT_LIMIT, DEFAULT_OFFSET
from cellar_wrapper.errors import CellarNotFoundError
from cellar_wrapper.models import (
    ActDetail,
    ActRef,
    EurovocTag,
    ExpressionItem,
    ListResult,
    RelationItem,
    SubjectMatterTag,
)
from cellar_wrapper.parser import (
    parse_act_detail,
    parse_act_refs,
    parse_bindings,
    parse_eurovoc_tags,
    parse_expressions,
    parse_relation_items,
    parse_subject_matter_tags,
)
from cellar_wrapper.sparql import (
    build_concept_query,
    build_expressions_query,
    build_get_act_query,
    build_legal_basis_query,
    build_resolve_celex_query,
)


class LookupMixin:
    """Methods for CELEX resolution and basic metadata."""

    def resolve_celex(self: ClientOpsProtocol, celex: str) -> ActRef:
        normalized = self._normalize_celex(celex)

        exact_query = build_resolve_celex_query(normalized, use_contains=False)
        rows = parse_bindings(self._transport.query_sparql(exact_query))
        if not rows:
            fallback_query = build_resolve_celex_query(normalized, use_contains=True)
            rows = parse_bindings(self._transport.query_sparql(fallback_query))

        if not rows:
            raise CellarNotFoundError(f"CELEX not found in CELLAR: {normalized}")

        refs = parse_act_refs(rows)
        for ref in refs:
            if ref.celex and ref.celex.upper() == normalized:
                return ref
        raise CellarNotFoundError(f"Fallback did not return exact CELEX match: {normalized}")

    def get_act(self: ClientOpsProtocol, celex: str, *, lang: str = DEFAULT_LANGUAGE) -> ActDetail:
        normalized_lang = self._normalize_lang(lang)
        work_uri = self._resolve_work_uri(celex)
        query = build_get_act_query(work_uri, lang=normalized_lang)
        rows = parse_bindings(self._transport.query_sparql(query))
        detail = parse_act_detail(rows)
        if detail is None:
            raise CellarNotFoundError(f"No act metadata for CELEX: {celex}")
        return detail

    def get_eurovoc(
        self: ClientOpsProtocol,
        celex: str,
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
    ) -> ListResult[EurovocTag]:
        self._validate_pagination(limit, offset)
        query = build_concept_query(
            self._resolve_work_uri(celex),
            predicate="cdm:work_is_about_concept_eurovoc",
            limit=limit,
            offset=offset,
        )
        return self._run_list_query(
            query_name="get_eurovoc",
            query=query,
            parser=parse_eurovoc_tags,
            limit=limit,
            offset=offset,
        )

    def get_subject_matter(
        self: ClientOpsProtocol,
        celex: str,
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
    ) -> ListResult[SubjectMatterTag]:
        self._validate_pagination(limit, offset)
        query = build_concept_query(
            self._resolve_work_uri(celex),
            predicate="cdm:resource_legal_is_about_subject-matter",
            limit=limit,
            offset=offset,
        )
        return self._run_list_query(
            query_name="get_subject_matter",
            query=query,
            parser=parse_subject_matter_tags,
            limit=limit,
            offset=offset,
        )

    def get_legal_basis(
        self: ClientOpsProtocol,
        celex: str,
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
    ) -> ListResult[RelationItem]:
        self._validate_pagination(limit, offset)
        query = build_legal_basis_query(self._resolve_work_uri(celex), limit=limit, offset=offset)
        return self._run_list_query(
            query_name="get_legal_basis",
            query=query,
            parser=parse_relation_items,
            limit=limit,
            offset=offset,
        )

    def get_directory_codes(
        self: ClientOpsProtocol,
        celex: str,
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
    ) -> ListResult[SubjectMatterTag]:
        self._validate_pagination(limit, offset)
        query = build_concept_query(
            self._resolve_work_uri(celex),
            predicate="cdm:resource_legal_id_directory-code",
            limit=limit,
            offset=offset,
        )
        return self._run_list_query(
            query_name="get_directory_codes",
            query=query,
            parser=parse_subject_matter_tags,
            limit=limit,
            offset=offset,
        )

    def get_expressions(
        self: ClientOpsProtocol,
        celex: str,
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
    ) -> ListResult[ExpressionItem]:
        self._validate_pagination(limit, offset)
        query = build_expressions_query(self._resolve_work_uri(celex), limit=limit, offset=offset)
        return self._run_list_query(
            query_name="get_expressions",
            query=query,
            parser=parse_expressions,
            limit=limit,
            offset=offset,
        )
