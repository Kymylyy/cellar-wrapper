"""Shared return-contract metadata for public client methods."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cellar_wrapper.models import (
    ActDetail,
    ActRef,
    ArticleAnnotationItem,
    CaseLawItem,
    DocumentPayload,
    DossierItem,
    EurovocTag,
    ExpressionItem,
    ListResult,
    NIMItem,
    RelationItem,
    SubjectMatterTag,
)


@dataclass(frozen=True)
class ReturnContract:
    return_type: type[Any]
    item_type: type[Any] | None = None
    query_name: str | None = None


RELATION_METHODS = frozenset(
    {
        "get_adopted_act",
        "get_ag_opinions",
        "get_amendments",
        "get_citations",
        "get_completing_acts",
        "get_consolidated_versions",
        "get_corrigenda",
        "get_deadlines",
        "get_delegated_acts",
        "get_legal_basis",
        "get_opinions",
        "get_other_relations",
        "get_proposals_to_amend",
        "get_related_works",
        "get_repeals",
        "new_amendments",
        "new_citations",
        "new_consolidated",
        "new_corrigenda",
        "new_delegated_acts",
        "new_proposals_to_amend",
        "new_repeals",
    }
)
ARTICLE_ANNOTATION_METHODS = frozenset({"get_article_annotations"})
CASE_METHODS = frozenset(
    {
        "get_cjeu_judgments",
        "get_national_decisions",
        "get_preliminary_questions",
        "new_case_law",
        "new_preliminary_questions",
    }
)
DOSSIER_METHODS = frozenset({"get_dossier"})
NIM_METHODS = frozenset({"get_nims", "new_nims"})
LOOKUP_CONCEPT_METHODS = frozenset({"get_eurovoc", "find_eurovoc_concept"})
SUBJECT_METHODS = frozenset({"get_subject_matter", "get_directory_codes"})
EXPRESSION_METHODS = frozenset({"get_expressions"})
ACT_SEARCH_METHODS = frozenset(
    {
        "search_by_eurovoc",
        "search_by_subject_matter",
        "search_by_title",
        "search_communications",
        "new_by_eurovoc",
    }
)


def _build_contracts() -> dict[str, ReturnContract]:
    contracts: dict[str, ReturnContract] = {
        "resolve_celex": ReturnContract(ActRef),
        "get_act": ReturnContract(ActDetail),
        "get_text": ReturnContract(DocumentPayload),
        "get_summary": ReturnContract(DocumentPayload),
    }
    for method_name in RELATION_METHODS:
        contracts[method_name] = ReturnContract(ListResult, item_type=RelationItem, query_name=method_name)
    for method_name in ARTICLE_ANNOTATION_METHODS:
        contracts[method_name] = ReturnContract(
            ListResult,
            item_type=ArticleAnnotationItem,
            query_name=method_name,
        )
    for method_name in CASE_METHODS:
        contracts[method_name] = ReturnContract(ListResult, item_type=CaseLawItem, query_name=method_name)
    for method_name in DOSSIER_METHODS:
        contracts[method_name] = ReturnContract(ListResult, item_type=DossierItem, query_name=method_name)
    for method_name in NIM_METHODS:
        contracts[method_name] = ReturnContract(ListResult, item_type=NIMItem, query_name=method_name)
    for method_name in LOOKUP_CONCEPT_METHODS:
        contracts[method_name] = ReturnContract(ListResult, item_type=EurovocTag, query_name=method_name)
    for method_name in SUBJECT_METHODS:
        contracts[method_name] = ReturnContract(
            ListResult,
            item_type=SubjectMatterTag,
            query_name=method_name,
        )
    for method_name in EXPRESSION_METHODS:
        contracts[method_name] = ReturnContract(ListResult, item_type=ExpressionItem, query_name=method_name)
    for method_name in ACT_SEARCH_METHODS:
        contracts[method_name] = ReturnContract(ListResult, item_type=ActRef, query_name=method_name)
    return contracts


RETURN_CONTRACTS = _build_contracts()

__all__ = ["RETURN_CONTRACTS", "ReturnContract"]
