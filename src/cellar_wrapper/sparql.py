"""Public SPARQL builder API (facade over modular query builders)."""

from cellar_wrapper.sparql_builders.common import PredicateSpec
from cellar_wrapper.sparql_builders.download import build_summary_lookup_query
from cellar_wrapper.sparql_builders.lookup import (
    build_concept_query,
    build_expressions_query,
    build_get_act_query,
    build_legal_basis_query,
    build_resolve_celex_query,
)
from cellar_wrapper.sparql_builders.relations import (
    build_ag_opinions_query,
    build_article_annotations_query,
    build_deadlines_query,
    build_dossier_query,
    build_national_decisions_query,
    build_relation_query,
)
from cellar_wrapper.sparql_builders.search import (
    build_find_eurovoc_concept_query,
    build_search_by_eurovoc_query,
    build_search_by_subject_matter_query,
    build_search_by_title_query,
    build_search_communications_query,
)

__all__ = [
    "PredicateSpec",
    "build_resolve_celex_query",
    "build_get_act_query",
    "build_concept_query",
    "build_legal_basis_query",
    "build_expressions_query",
    "build_relation_query",
    "build_dossier_query",
    "build_deadlines_query",
    "build_ag_opinions_query",
    "build_national_decisions_query",
    "build_article_annotations_query",
    "build_search_by_eurovoc_query",
    "build_search_by_subject_matter_query",
    "build_search_by_title_query",
    "build_search_communications_query",
    "build_find_eurovoc_concept_query",
    "build_summary_lookup_query",
]
