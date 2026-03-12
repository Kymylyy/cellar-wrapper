"""CLI command specifications."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CommandSpec:
    group: str
    command: str
    method: str
    requires_celex: bool = False
    requires_since: bool = False
    has_since: bool = False
    has_resource_type: bool = False
    has_country: bool = False
    has_lang: bool = False
    has_direction: bool = False
    has_limit_offset: bool = False
    has_format: bool = False
    list_arg_name: str | None = None
    scalar_arg_name: str | None = None


COMMANDS: list[CommandSpec] = [
    CommandSpec("lookup", "resolve-celex", "resolve_celex", requires_celex=True),
    CommandSpec("lookup", "get-act", "get_act", requires_celex=True, has_lang=True),
    CommandSpec("lookup", "get-eurovoc", "get_eurovoc", requires_celex=True, has_limit_offset=True),
    CommandSpec("lookup", "get-subject-matter", "get_subject_matter", requires_celex=True, has_limit_offset=True),
    CommandSpec("lookup", "get-legal-basis", "get_legal_basis", requires_celex=True, has_limit_offset=True),
    CommandSpec("lookup", "get-directory-codes", "get_directory_codes", requires_celex=True, has_limit_offset=True),
    CommandSpec("lookup", "get-expressions", "get_expressions", requires_celex=True, has_limit_offset=True),
    CommandSpec("relations", "get-amendments", "get_amendments", requires_celex=True, has_since=True, has_resource_type=True, has_lang=True, has_direction=True, has_limit_offset=True),
    CommandSpec("relations", "get-repeals", "get_repeals", requires_celex=True, has_since=True, has_resource_type=True, has_lang=True, has_direction=True, has_limit_offset=True),
    CommandSpec("relations", "get-citations", "get_citations", requires_celex=True, has_since=True, has_resource_type=True, has_lang=True, has_direction=True, has_limit_offset=True),
    CommandSpec("relations", "get-based-on-acts", "get_based_on_acts", requires_celex=True, has_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("relations", "get-completing-acts", "get_completing_acts", requires_celex=True, has_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("relations", "get-proposals-to-amend", "get_proposals_to_amend", requires_celex=True, has_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("relations", "get-adopted-act", "get_adopted_act", requires_celex=True, has_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("relations", "get-related-works", "get_related_works", requires_celex=True, has_since=True, has_resource_type=True, has_lang=True, has_direction=True, has_limit_offset=True),
    CommandSpec("relations", "get-other-relations", "get_other_relations", requires_celex=True, has_since=True, has_resource_type=True, has_lang=True, has_direction=True, has_limit_offset=True),
    CommandSpec("lifecycle", "get-consolidated-versions", "get_consolidated_versions", requires_celex=True, has_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("lifecycle", "get-corrigenda", "get_corrigenda", requires_celex=True, has_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("lifecycle", "get-nims", "get_nims", requires_celex=True, has_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("lifecycle", "get-dossier", "get_dossier", requires_celex=True, has_lang=True, has_limit_offset=True),
    CommandSpec("lifecycle", "get-opinions", "get_opinions", requires_celex=True, has_since=True, has_lang=True, has_limit_offset=True),
    CommandSpec("lifecycle", "get-deadlines", "get_deadlines", requires_celex=True, has_limit_offset=True),
    CommandSpec("case-law", "get-cjeu-judgments", "get_cjeu_judgments", requires_celex=True, has_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("case-law", "get-ag-opinions", "get_ag_opinions", requires_celex=True, has_since=True, has_lang=True, has_limit_offset=True),
    CommandSpec("case-law", "get-preliminary-questions", "get_preliminary_questions", requires_celex=True, has_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("case-law", "get-national-decisions", "get_national_decisions", requires_celex=True, has_since=True, has_country=True, has_lang=True, has_limit_offset=True),
    CommandSpec("case-law", "get-article-annotations", "get_article_annotations", requires_celex=True, has_limit_offset=True),
    CommandSpec("search", "search-by-eurovoc", "search_by_eurovoc", has_since=True, list_arg_name="tags", has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("search", "search-by-subject-matter", "search_by_subject_matter", has_since=True, list_arg_name="codes", has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("search", "search-by-title", "search_by_title", has_since=True, scalar_arg_name="keyword", has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("search", "search-communications", "search_communications", has_since=True, scalar_arg_name="dg", has_lang=True, has_limit_offset=True),
    CommandSpec("search", "find-eurovoc-concept", "find_eurovoc_concept", scalar_arg_name="label", has_limit_offset=True),
    CommandSpec("monitoring", "new-citations", "new_citations", requires_celex=True, requires_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("monitoring", "new-amendments", "new_amendments", requires_celex=True, requires_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("monitoring", "new-repeals", "new_repeals", requires_celex=True, requires_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("monitoring", "new-proposals-to-amend", "new_proposals_to_amend", requires_celex=True, requires_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("monitoring", "new-based-on-acts", "new_based_on_acts", requires_celex=True, requires_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("monitoring", "new-case-law", "new_case_law", requires_celex=True, requires_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("monitoring", "new-preliminary-questions", "new_preliminary_questions", requires_celex=True, requires_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("monitoring", "new-corrigenda", "new_corrigenda", requires_celex=True, requires_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("monitoring", "new-consolidated", "new_consolidated", requires_celex=True, requires_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("monitoring", "new-nims", "new_nims", requires_celex=True, requires_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("monitoring", "new-by-eurovoc", "new_by_eurovoc", requires_since=True, list_arg_name="tags", has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("download", "get-text", "get_text", requires_celex=True, has_lang=True, has_format=True),
    CommandSpec("download", "get-summary", "get_summary", requires_celex=True, has_lang=True),
]
