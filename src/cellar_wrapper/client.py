"""Public sync client for CELLAR wrapper."""

from __future__ import annotations

import base64
import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any, TypeVar, cast

from cellar_wrapper.constants import (
    DEFAULT_LANGUAGE,
    DEFAULT_LIMIT,
    DEFAULT_OFFSET,
    DEFAULT_RESOURCE_BASE_URL,
    DEFAULT_RETRIES,
    DEFAULT_SPARQL_ENDPOINT,
    MAX_LIMIT,
    PREDICATES,
    SUMMARY_ACCEPT,
    TEXT_FORMAT_ACCEPT,
)
from cellar_wrapper.errors import CellarNotFoundError, CellarValidationError
from cellar_wrapper.http import HttpTransport, TimeoutConfig
from cellar_wrapper.models import (
    ActDetail,
    ActRef,
    CaseLawItem,
    DocumentPayload,
    EurovocTag,
    ExpressionItem,
    ListResult,
    QueryMeta,
    RelationItem,
    SubjectMatterTag,
)
from cellar_wrapper.parser import (
    parse_act_detail,
    parse_act_refs,
    parse_bindings,
    parse_case_law_items,
    parse_eurovoc_tags,
    parse_expressions,
    parse_relation_items,
    parse_subject_matter_tags,
)
from cellar_wrapper.sparql import (
    PredicateSpec,
    build_ag_opinions_query,
    build_article_annotations_query,
    build_concept_query,
    build_deadlines_query,
    build_dossier_query,
    build_expressions_query,
    build_find_eurovoc_concept_query,
    build_get_act_query,
    build_legal_basis_query,
    build_national_decisions_query,
    build_relation_query,
    build_resolve_celex_query,
    build_search_by_eurovoc_query,
    build_search_by_subject_matter_query,
    build_search_by_title_query,
    build_search_communications_query,
    build_summary_lookup_query,
)

CELEX_RE = re.compile(r"^[0-9A-Z()_\-]{5,40}$")
LANG_RE = re.compile(r"^[a-zA-Z]{3}$")
RESOURCE_TYPE_RE = re.compile(r"^[A-Z_]+$")

T = TypeVar("T")


@dataclass(frozen=True)
class _RelationCallSpec:
    predicates: Sequence[PredicateSpec]
    direction: str
    default_resource_type: str | None = None
    case_law: bool = False


_RELATION_CALL_SPECS: dict[str, _RelationCallSpec] = {
    "get_amendments": _RelationCallSpec([PredicateSpec(PREDICATES["amends"], "amends")], "both"),
    "get_repeals": _RelationCallSpec(
        [
            PredicateSpec(PREDICATES["repeals"], "repeals"),
            PredicateSpec(PREDICATES["implicitly_repeals"], "implicitly_repeals"),
        ],
        "both",
    ),
    "get_citations": _RelationCallSpec([PredicateSpec(PREDICATES["cites"], "cites")], "both"),
    "get_delegated_acts": _RelationCallSpec(
        [PredicateSpec(PREDICATES["based_on"], "based_on")], "incoming"
    ),
    "get_completing_acts": _RelationCallSpec(
        [PredicateSpec(PREDICATES["completes"], "completes")], "incoming"
    ),
    "get_proposals_to_amend": _RelationCallSpec(
        [PredicateSpec(PREDICATES["proposes_to_amend"], "proposes_to_amend")], "incoming"
    ),
    "get_adopted_act": _RelationCallSpec([PredicateSpec(PREDICATES["adopts"], "adopts")], "incoming"),
    "get_related_works": _RelationCallSpec(
        [PredicateSpec(PREDICATES["related"], "related")],
        "both",
    ),
    "get_other_relations": _RelationCallSpec(
        [
            PredicateSpec(PREDICATES["suspends"], "suspends"),
            PredicateSpec(PREDICATES["partially_suspends"], "partially_suspends"),
            PredicateSpec(PREDICATES["defers_application"], "defers_application"),
            PredicateSpec(PREDICATES["renders_obsolete"], "renders_obsolete"),
            PredicateSpec(PREDICATES["influences"], "influences"),
        ],
        "both",
    ),
    "get_consolidated_versions": _RelationCallSpec(
        [PredicateSpec(PREDICATES["consolidates"], "consolidates")],
        "incoming",
        default_resource_type="CONS_TEXT",
    ),
    "get_corrigenda": _RelationCallSpec(
        [PredicateSpec(PREDICATES["corrects"], "corrects")],
        "incoming",
    ),
    "get_nims": _RelationCallSpec(
        [PredicateSpec(PREDICATES["nims"], "nims")],
        "incoming",
        default_resource_type="MEAS_NATION_IMPL",
    ),
    "get_cjeu_judgments": _RelationCallSpec(
        [PredicateSpec(PREDICATES["cjeu_interprets"], "cjeu_interprets")],
        "incoming",
        default_resource_type="JUDG",
        case_law=True,
    ),
    "get_preliminary_questions": _RelationCallSpec(
        [PredicateSpec(PREDICATES["preliminary_questions"], "preliminary_questions")],
        "incoming",
        case_law=True,
    ),
    "new_citations": _RelationCallSpec([PredicateSpec(PREDICATES["cites"], "cites")], "incoming"),
    "new_amendments": _RelationCallSpec([PredicateSpec(PREDICATES["amends"], "amends")], "incoming"),
    "new_delegated_acts": _RelationCallSpec(
        [PredicateSpec(PREDICATES["based_on"], "based_on")],
        "incoming",
    ),
    "new_case_law": _RelationCallSpec(
        [PredicateSpec(PREDICATES["cjeu_interprets"], "cjeu_interprets")],
        "incoming",
        default_resource_type="JUDG",
        case_law=True,
    ),
    "new_corrigenda": _RelationCallSpec(
        [PredicateSpec(PREDICATES["corrects"], "corrects")],
        "incoming",
    ),
    "new_consolidated": _RelationCallSpec(
        [PredicateSpec(PREDICATES["consolidates"], "consolidates")],
        "incoming",
        default_resource_type="CONS_TEXT",
    ),
    "new_nims": _RelationCallSpec(
        [PredicateSpec(PREDICATES["nims"], "nims")],
        "incoming",
        default_resource_type="MEAS_NATION_IMPL",
    ),
}


class CellarClient:
    """Sync-first API client for CELLAR."""

    def __init__(
        self,
        *,
        base_url_sparql: str = DEFAULT_SPARQL_ENDPOINT,
        base_url_resource: str = DEFAULT_RESOURCE_BASE_URL,
        timeout: TimeoutConfig | None = None,
        retries: int = DEFAULT_RETRIES,
        user_agent: str = "cellar-wrapper/0.1.0",
        transport: HttpTransport | None = None,
    ) -> None:
        self._base_url_resource = base_url_resource.rstrip("/")
        self._transport = transport or HttpTransport(
            sparql_endpoint=base_url_sparql,
            retries=retries,
            user_agent=user_agent,
            timeout=timeout,
        )

    def close(self) -> None:
        """Close underlying HTTP resources."""
        self._transport.close()

    def _normalize_celex(self, celex: str) -> str:
        normalized = celex.strip().upper()
        if not CELEX_RE.fullmatch(normalized):
            raise CellarValidationError(f"Invalid CELEX identifier: {celex!r}")
        return normalized

    def _normalize_lang(self, lang: str) -> str:
        normalized = lang.strip().lower()
        if not LANG_RE.fullmatch(normalized):
            raise CellarValidationError(f"Invalid language code: {lang!r}")
        return normalized

    def _normalize_resource_type(self, resource_type: str | None) -> str | None:
        if resource_type is None:
            return None
        normalized = resource_type.strip().upper()
        if not RESOURCE_TYPE_RE.fullmatch(normalized):
            raise CellarValidationError(f"Invalid resource_type: {resource_type!r}")
        return normalized

    def _coerce_since(self, since: date | datetime | str | None) -> str | None:
        if since is None:
            return None
        if isinstance(since, datetime):
            return since.isoformat()
        if isinstance(since, date):
            return since.isoformat()

        candidate = since.strip()
        candidate_for_parse = candidate.replace("Z", "+00:00")
        try:
            datetime.fromisoformat(candidate_for_parse)
            return candidate
        except ValueError:
            pass

        try:
            date.fromisoformat(candidate)
            return candidate
        except ValueError as exc:
            raise CellarValidationError(
                f"Invalid since value (expected ISO date/datetime): {since!r}"
            ) from exc

    @staticmethod
    def _validate_pagination(limit: int, offset: int) -> None:
        if limit <= 0:
            raise CellarValidationError("limit must be > 0")
        if limit > MAX_LIMIT:
            raise CellarValidationError(f"limit cannot exceed {MAX_LIMIT}")
        if offset < 0:
            raise CellarValidationError("offset cannot be negative")

    def _meta(self, query_name: str, *, limit: int | None, offset: int | None) -> QueryMeta:
        return QueryMeta(
            query_name=query_name,
            endpoint=self._transport.sparql_endpoint,
            executed_at=datetime.now(UTC),
            limit=limit,
            offset=offset,
        )

    def _list_result(
        self,
        *,
        query_name: str,
        items: list[T],
        limit: int | None,
        offset: int | None,
    ) -> ListResult[T]:
        return ListResult[T](
            items=items,
            returned_count=len(items),
            meta=self._meta(query_name, limit=limit, offset=offset),
        )

    def _resolve_work_uri(self, celex: str) -> str:
        return self.resolve_celex(celex).uri

    def _call_relation(
        self,
        *,
        method_name: str,
        celex: str,
        since: date | datetime | str | None,
        resource_type: str | None,
        limit: int,
        offset: int,
        lang: str,
    ) -> ListResult[RelationItem] | ListResult[CaseLawItem]:
        spec = _RELATION_CALL_SPECS[method_name]
        self._validate_pagination(limit, offset)
        normalized_lang = self._normalize_lang(lang)
        normalized_type = self._normalize_resource_type(resource_type) or spec.default_resource_type
        since_value = self._coerce_since(since)
        work_uri = self._resolve_work_uri(celex)

        query = build_relation_query(
            work_uri,
            predicates=spec.predicates,
            direction=spec.direction,
            since=since_value,
            resource_type=normalized_type,
            limit=limit,
            offset=offset,
            lang=normalized_lang,
        )
        rows = parse_bindings(self._transport.query_sparql(query))

        if spec.case_law:
            case_items = parse_case_law_items(rows)
            return self._list_result(
                query_name=method_name,
                items=case_items,
                limit=limit,
                offset=offset,
            )

        relation_items = parse_relation_items(rows)
        return self._list_result(
            query_name=method_name,
            items=relation_items,
            limit=limit,
            offset=offset,
        )

    # Explicit methods (non-generic shapes)
    def resolve_celex(self, celex: str) -> ActRef:
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
        return refs[0]

    def get_act(self, celex: str, *, lang: str = DEFAULT_LANGUAGE) -> ActDetail:
        normalized_lang = self._normalize_lang(lang)
        work_uri = self._resolve_work_uri(celex)
        query = build_get_act_query(work_uri, lang=normalized_lang)
        rows = parse_bindings(self._transport.query_sparql(query))
        detail = parse_act_detail(rows)
        if detail is None:
            raise CellarNotFoundError(f"No act metadata for CELEX: {celex}")
        return detail

    def get_eurovoc(
        self,
        celex: str,
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
    ) -> ListResult[EurovocTag]:
        self._validate_pagination(limit, offset)
        query = build_concept_query(self._resolve_work_uri(celex), predicate="cdm:work_is_about_concept_eurovoc")
        rows = parse_bindings(self._transport.query_sparql(query))
        return self._list_result(
            query_name="get_eurovoc",
            items=parse_eurovoc_tags(rows),
            limit=limit,
            offset=offset,
        )

    def get_subject_matter(
        self,
        celex: str,
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
    ) -> ListResult[SubjectMatterTag]:
        self._validate_pagination(limit, offset)
        query = build_concept_query(
            self._resolve_work_uri(celex),
            predicate="cdm:resource_legal_is_about_subject-matter",
        )
        rows = parse_bindings(self._transport.query_sparql(query))
        return self._list_result(
            query_name="get_subject_matter",
            items=parse_subject_matter_tags(rows),
            limit=limit,
            offset=offset,
        )

    def get_legal_basis(
        self,
        celex: str,
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
    ) -> ListResult[RelationItem]:
        self._validate_pagination(limit, offset)
        query = build_legal_basis_query(self._resolve_work_uri(celex), limit=limit, offset=offset)
        rows = parse_bindings(self._transport.query_sparql(query))
        return self._list_result(
            query_name="get_legal_basis",
            items=parse_relation_items(rows),
            limit=limit,
            offset=offset,
        )

    def get_directory_codes(
        self,
        celex: str,
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
    ) -> ListResult[SubjectMatterTag]:
        self._validate_pagination(limit, offset)
        query = build_concept_query(
            self._resolve_work_uri(celex),
            predicate="cdm:resource_legal_id_directory-code",
        )
        rows = parse_bindings(self._transport.query_sparql(query))
        return self._list_result(
            query_name="get_directory_codes",
            items=parse_subject_matter_tags(rows),
            limit=limit,
            offset=offset,
        )

    def get_expressions(
        self,
        celex: str,
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
    ) -> ListResult[ExpressionItem]:
        self._validate_pagination(limit, offset)
        query = build_expressions_query(self._resolve_work_uri(celex), limit=limit, offset=offset)
        rows = parse_bindings(self._transport.query_sparql(query))
        return self._list_result(
            query_name="get_expressions",
            items=parse_expressions(rows),
            limit=limit,
            offset=offset,
        )

    def get_dossier(
        self,
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
        rows = parse_bindings(self._transport.query_sparql(query))
        return self._list_result(
            query_name="get_dossier",
            items=parse_relation_items(rows),
            limit=limit,
            offset=offset,
        )

    def get_opinions(
        self,
        celex: str,
        *,
        since: date | datetime | str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[RelationItem]:
        return cast(
            ListResult[RelationItem],
            self._call_relation(
            method_name="get_opinions",
            celex=celex,
            since=since,
            resource_type=None,
            limit=limit,
            offset=offset,
            lang=lang,
            ),
        )

    def get_deadlines(
        self,
        celex: str,
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
    ) -> ListResult[RelationItem]:
        self._validate_pagination(limit, offset)
        query = build_deadlines_query(self._resolve_work_uri(celex), limit=limit, offset=offset)
        rows = parse_bindings(self._transport.query_sparql(query))
        return self._list_result(
            query_name="get_deadlines",
            items=parse_relation_items(rows),
            limit=limit,
            offset=offset,
        )

    def get_ag_opinions(
        self,
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

    def get_national_decisions(
        self,
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
        self,
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

    def search_by_eurovoc(
        self,
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
        self,
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
        self,
        keyword: str,
        *,
        resource_type: str | None = None,
        since: date | datetime | str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> ListResult[ActRef]:
        self._validate_pagination(limit, offset)
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
        self,
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
        self,
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

    def new_by_eurovoc(
        self,
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
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    def get_text(
        self,
        celex: str,
        *,
        lang: str = DEFAULT_LANGUAGE,
        format: str = "pdf",
    ) -> DocumentPayload:
        normalized_celex = self._normalize_celex(celex)
        normalized_lang = self._normalize_lang(lang)
        format_key = format.strip().lower()
        if format_key not in TEXT_FORMAT_ACCEPT:
            raise CellarValidationError(f"Unsupported format: {format!r}")

        content, content_type, source_url = self._transport.download(
            f"{self._base_url_resource}/celex/{normalized_celex}",
            accept=TEXT_FORMAT_ACCEPT[format_key],
            language=normalized_lang,
        )
        return DocumentPayload(
            source_url=source_url,
            content_type=content_type,
            language=normalized_lang,
            content_base64=base64.b64encode(content).decode("ascii"),
        )

    def get_summary(self, celex: str, *, lang: str = DEFAULT_LANGUAGE) -> DocumentPayload:
        normalized_lang = self._normalize_lang(lang)
        summary_query = build_summary_lookup_query(self._resolve_work_uri(celex))
        rows = parse_bindings(self._transport.query_sparql(summary_query))
        if not rows:
            raise CellarNotFoundError(f"No legislative summary found for CELEX: {celex}")

        summary_uri = parse_act_refs(rows)[0].uri
        content, content_type, source_url = self._transport.download(
            summary_uri,
            accept=SUMMARY_ACCEPT,
            language=normalized_lang,
        )
        return DocumentPayload(
            source_url=source_url,
            content_type=content_type,
            language=normalized_lang,
            content_base64=base64.b64encode(content).decode("ascii"),
        )


# Dynamically attach simple relation methods with shared signature.
def _make_relation_method(method_name: str, *, require_since: bool) -> Callable[..., Any]:
    def _method(
        self: CellarClient,
        celex: str,
        since: date | datetime | str | None = None,
        *,
        resource_type: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        lang: str = DEFAULT_LANGUAGE,
    ) -> Any:
        if require_since and since is None:
            raise CellarValidationError(f"{method_name} requires since")
        return self._call_relation(
            method_name=method_name,
            celex=celex,
            since=since,
            resource_type=resource_type,
            limit=limit,
            offset=offset,
            lang=lang,
        )

    _method.__name__ = method_name
    _method.__qualname__ = f"CellarClient.{method_name}"
    _method.__doc__ = f"Auto-generated wrapper for {method_name}."
    return _method


for _name in _RELATION_CALL_SPECS:
    if _name == "get_opinions":
        # get_opinions has explicit implementation with custom predicate set.
        continue
    setattr(CellarClient, _name, _make_relation_method(_name, require_since=_name.startswith("new_")))


# Custom relation spec for get_opinions after dynamic method map is created.
_RELATION_CALL_SPECS["get_opinions"] = _RelationCallSpec(
    [
        PredicateSpec("cdm:resource_legal_contains_eesc_opinion_on_resource_legal", "eesc_opinion"),
        PredicateSpec("cdm:resource_legal_contains_ep_opinion_on_resource_legal", "ep_opinion"),
        PredicateSpec(PREDICATES["influences"], "influences"),
    ],
    "incoming",
)
