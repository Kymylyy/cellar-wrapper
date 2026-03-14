"""CLI command specifications."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from cellar_wrapper.constants import DEFAULT_LANGUAGE, DEFAULT_LIMIT, DEFAULT_OFFSET
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

ParameterKind = Literal[
    "celex",
    "since",
    "to",
    "resource_types",
    "country",
    "lang",
    "direction",
    "limit",
    "offset",
    "format",
    "string",
    "string_list",
]

_NO_DEFAULT = object()


@dataclass(frozen=True)
class ReturnContract:
    return_type: type[Any]
    item_type: type[Any] | None = None
    query_name: str | None = None


@dataclass(frozen=True)
class CommandParameterSpec:
    name: str
    kind: ParameterKind
    help_text: str
    required: bool = False
    default: Any = _NO_DEFAULT
    choices: tuple[str, ...] | None = None

    @property
    def cli_option(self) -> str:
        return f"--{self.name.replace('_', '-')}"

    @property
    def is_list(self) -> bool:
        return self.kind in {"resource_types", "string_list"}

    @property
    def has_default(self) -> bool:
        return self.default is not _NO_DEFAULT


@dataclass(frozen=True)
class CommandSpec:
    group: str
    command: str
    method: str
    description: str
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

    @property
    def full_name(self) -> str:
        return f"{self.group} {self.command}"

    @property
    def return_contract(self) -> ReturnContract:
        return RETURN_CONTRACTS[self.method]

    @property
    def parameters(self) -> tuple[CommandParameterSpec, ...]:
        params: list[CommandParameterSpec] = []

        if self.requires_celex:
            params.append(
                CommandParameterSpec(
                    name="celex",
                    kind="celex",
                    help_text="CELEX identifier.",
                    required=True,
                )
            )

        if self.requires_since:
            params.append(
                CommandParameterSpec(
                    name="since",
                    kind="since",
                    help_text="Include items from this date/time.",
                    required=True,
                )
            )
        elif self.has_since:
            params.append(
                CommandParameterSpec(
                    name="since",
                    kind="since",
                    help_text="Optional lower date/time bound.",
                    default=None,
                )
            )

        if self.requires_since or self.has_since:
            params.append(
                CommandParameterSpec(
                    name="to",
                    kind="to",
                    help_text="Optional upper date/time bound.",
                    default=None,
                )
            )

        if self.has_resource_type:
            params.append(
                CommandParameterSpec(
                    name="resource_types",
                    kind="resource_types",
                    help_text="Filter by one or more CELLAR resource type tokens.",
                    default=None,
                )
            )
        if self.has_country:
            params.append(
                CommandParameterSpec(
                    name="country",
                    kind="country",
                    help_text="Filter by ISO-3 country code.",
                    default=None,
                )
            )
        if self.has_lang:
            params.append(
                CommandParameterSpec(
                    name="lang",
                    kind="lang",
                    help_text="Language code.",
                    default=DEFAULT_LANGUAGE,
                )
            )
        if self.has_direction:
            params.append(
                CommandParameterSpec(
                    name="direction",
                    kind="direction",
                    help_text="Relation direction to include.",
                    default="both",
                    choices=("incoming", "outgoing", "both"),
                )
            )
        if self.has_limit_offset:
            params.extend(
                (
                    CommandParameterSpec(
                        name="limit",
                        kind="limit",
                        help_text="Maximum number of items to return.",
                        default=DEFAULT_LIMIT,
                    ),
                    CommandParameterSpec(
                        name="offset",
                        kind="offset",
                        help_text="Number of items to skip before returning results.",
                        default=DEFAULT_OFFSET,
                    ),
                )
            )
        if self.has_format:
            params.append(
                CommandParameterSpec(
                    name="format",
                    kind="format",
                    help_text="Document format (for example pdf).",
                    default="pdf",
                    choices=("pdf", "xhtml", "xml", "rdf", "docx"),
                )
            )
        if self.list_arg_name is not None:
            params.append(
                CommandParameterSpec(
                    name=self.list_arg_name,
                    kind="string_list",
                    help_text=_list_arg_help(self.list_arg_name),
                    required=True,
                )
            )
        if self.scalar_arg_name is not None:
            params.append(
                CommandParameterSpec(
                    name=self.scalar_arg_name,
                    kind="string",
                    help_text=_scalar_arg_help(self.scalar_arg_name),
                    required=True,
                )
            )

        return tuple(params)

def _list_arg_help(arg_name: str) -> str:
    help_by_name = {
        "tags": "One or more EuroVoc tags.",
        "codes": "One or more subject-matter codes.",
    }
    return help_by_name.get(arg_name, f"One or more values for {arg_name}.")


def _scalar_arg_help(arg_name: str) -> str:
    help_by_name = {
        "keyword": "Title keyword to search.",
        "dg": "Directorate-General code (for example FISMA).",
        "label": "EuroVoc label to match.",
    }
    return help_by_name.get(arg_name, f"Value for {arg_name}.")


COMMANDS: list[CommandSpec] = [
    CommandSpec(
        "lookup",
        "resolve-celex",
        "resolve_celex",
        description="Resolve a CELEX identifier to the canonical CELLAR work reference.",
        requires_celex=True,
    ),
    CommandSpec(
        "lookup",
        "get-act",
        "get_act",
        description="Fetch the main metadata card for one act when you need title, type, dates, and institutions.",
        requires_celex=True,
        has_lang=True,
    ),
    CommandSpec(
        "lookup",
        "get-eurovoc",
        "get_eurovoc",
        description="List the EuroVoc concepts linked to one act.",
        requires_celex=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "lookup",
        "get-subject-matter",
        "get_subject_matter",
        description="List the subject-matter concepts linked to one act.",
        requires_celex=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "lookup",
        "get-legal-basis",
        "get_legal_basis",
        description="Inspect treaty basis and based-on relations, including delegated-act to base-act reverse lookup.",
        requires_celex=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "lookup",
        "get-directory-codes",
        "get_directory_codes",
        description="List directory-code concepts assigned to one act.",
        requires_celex=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "lookup",
        "get-expressions",
        "get_expressions",
        description="List language expressions and versions available for one act.",
        requires_celex=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-amendments",
        "get_amendments",
        description="Show amendment relations affecting or issued by the act.",
        requires_celex=True,
        has_since=True,
        has_resource_type=True,
        has_lang=True,
        has_direction=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-repeals",
        "get_repeals",
        description="Show explicit and implicit repeal relations affecting or issued by the act.",
        requires_celex=True,
        has_since=True,
        has_resource_type=True,
        has_lang=True,
        has_direction=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-citations",
        "get_citations",
        description="Show works that cite the act when you need broad legal and non-legal references.",
        requires_celex=True,
        has_since=True,
        has_resource_type=True,
        has_lang=True,
        has_direction=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-based-on-acts",
        "get_based_on_acts",
        description="Show the broad incoming based-on bucket for acts and documents derived from the act.",
        requires_celex=True,
        has_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-completing-acts",
        "get_completing_acts",
        description="Show the narrower completes relation for acts that supplement or complete the act.",
        requires_celex=True,
        has_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-proposals-to-change",
        "get_proposals_to_change",
        description="Show proposal acts that may amend, repeal, recast, or otherwise change the act.",
        requires_celex=True,
        has_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-adopted-act",
        "get_adopted_act",
        description="Show adopted acts linked to the act from proposal or precursor workflows.",
        requires_celex=True,
        has_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-related-works",
        "get_related_works",
        description="Show generic related-work links when no narrower relation command fits.",
        requires_celex=True,
        has_since=True,
        has_resource_type=True,
        has_lang=True,
        has_direction=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-other-relations",
        "get_other_relations",
        description="Inspect sparse catch-all legal relations such as suspend, defer, obsolete, or influence.",
        requires_celex=True,
        has_since=True,
        has_resource_type=True,
        has_lang=True,
        has_direction=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-article-annotations",
        "get_article_annotations",
        description="Retrieve OWL-style article annotations with article, paragraph, point, and legal-basis qualifiers.",
        requires_celex=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "lifecycle",
        "get-consolidated-versions",
        "get_consolidated_versions",
        description="List consolidated-text relations and aliases linked to the act.",
        requires_celex=True,
        has_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "lifecycle",
        "get-corrigenda",
        "get_corrigenda",
        description="List corrigenda linked to the act, defaulting to corrigendum-type rows.",
        requires_celex=True,
        has_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "lifecycle",
        "get-nims",
        "get_nims",
        description="List grouped national implementing measures for a directive or other implementation-driven act.",
        requires_celex=True,
        has_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "lifecycle",
        "get-dossier",
        "get_dossier",
        description="List other documents in the act's dossier when you need the dossier feed rather than a timeline.",
        requires_celex=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "lifecycle",
        "get-opinions",
        "get_opinions",
        description="Show opinion-like and influence-like rows, most useful on proposals and legislative packages.",
        requires_celex=True,
        has_since=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "lifecycle",
        "get-deadlines",
        "get_deadlines",
        description="List deadline and date-fact rows attached to the act itself.",
        requires_celex=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "case-law",
        "get-cjeu-judgments",
        "get_cjeu_judgments",
        description="List CJEU judgments interpreting the act.",
        requires_celex=True,
        has_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "case-law",
        "get-ag-opinions",
        "get_ag_opinions",
        description="List Advocate General opinions linked to the act as a relation feed rather than a case-law payload.",
        requires_celex=True,
        has_since=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "case-law",
        "get-preliminary-questions",
        "get_preliminary_questions",
        description="List preliminary questions submitted about the act, often with sparse INFO_JUDICIAL metadata.",
        requires_celex=True,
        has_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "case-law",
        "get-national-decisions",
        "get_national_decisions",
        description="List national decisions referencing the act by CELEX mention, optionally filtered by country.",
        requires_celex=True,
        has_since=True,
        has_country=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "search",
        "search-by-eurovoc",
        "search_by_eurovoc",
        description="Find acts by EuroVoc tags after local concept resolution.",
        has_since=True,
        list_arg_name="tags",
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "search",
        "search-by-subject-matter",
        "search_by_subject_matter",
        description="Find acts by subject-matter codes or labels after local concept resolution.",
        has_since=True,
        list_arg_name="codes",
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "search",
        "search-by-title",
        "search_by_title",
        description="Find acts by title keyword with optional type and date filtering.",
        has_since=True,
        scalar_arg_name="keyword",
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "search",
        "search-communications",
        "search_communications",
        description="Find Commission communications by DG when you want policy and preparatory signals rather than legislation.",
        has_since=True,
        scalar_arg_name="dg",
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "search",
        "find-eurovoc-concept",
        "find_eurovoc_concept",
        description="Search the packaged local EuroVoc index for concepts matching a label.",
        scalar_arg_name="label",
        has_limit_offset=True,
    ),
    CommandSpec(
        "monitoring",
        "new-citations",
        "new_citations",
        description="Monitor new citation rows for the act since a required lower date bound.",
        requires_celex=True,
        requires_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "monitoring",
        "new-amendments",
        "new_amendments",
        description="Monitor new amendment rows for the act since a required lower date bound.",
        requires_celex=True,
        requires_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "monitoring",
        "new-repeals",
        "new_repeals",
        description="Monitor new repeal rows for the act since a required lower date bound.",
        requires_celex=True,
        requires_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "monitoring",
        "new-proposals-to-change",
        "new_proposals_to_change",
        description="Monitor new proposals that may change the act since a required lower date bound.",
        requires_celex=True,
        requires_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "monitoring",
        "new-based-on-acts",
        "new_based_on_acts",
        description="Monitor new acts and documents derived from the act via the broad based-on relation.",
        requires_celex=True,
        requires_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "monitoring",
        "new-case-law",
        "new_case_law",
        description="Monitor new CJEU case-law items linked to the act since a required lower date bound.",
        requires_celex=True,
        requires_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "monitoring",
        "new-preliminary-questions",
        "new_preliminary_questions",
        description="Monitor new preliminary questions linked to the act since a required lower date bound.",
        requires_celex=True,
        requires_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "monitoring",
        "new-corrigenda",
        "new_corrigenda",
        description="Monitor new corrigenda linked to the act since a required lower date bound.",
        requires_celex=True,
        requires_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "monitoring",
        "new-consolidated",
        "new_consolidated",
        description="Monitor new consolidated-text relations linked to the act since a required lower date bound.",
        requires_celex=True,
        requires_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "monitoring",
        "new-nims",
        "new_nims",
        description="Monitor new grouped national implementing measures since a required lower date bound.",
        requires_celex=True,
        requires_since=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "monitoring",
        "new-by-eurovoc",
        "new_by_eurovoc",
        description="Monitor new acts by EuroVoc tags since a required lower date bound.",
        requires_since=True,
        list_arg_name="tags",
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "download",
        "get-text",
        "get_text",
        description="Download the full text of an act in the requested format and language.",
        requires_celex=True,
        has_lang=True,
        has_format=True,
    ),
    CommandSpec(
        "download",
        "get-summary",
        "get_summary",
        description="Download the official summary for an act in the requested language.",
        requires_celex=True,
        has_lang=True,
    ),
]


_RELATION_METHODS = frozenset(
    {
        "get_adopted_act",
        "get_ag_opinions",
        "get_amendments",
        "get_citations",
        "get_completing_acts",
        "get_consolidated_versions",
        "get_corrigenda",
        "get_deadlines",
        "get_based_on_acts",
        "get_legal_basis",
        "get_opinions",
        "get_other_relations",
        "get_proposals_to_change",
        "get_related_works",
        "get_repeals",
        "new_amendments",
        "new_citations",
        "new_consolidated",
        "new_corrigenda",
        "new_based_on_acts",
        "new_proposals_to_change",
        "new_repeals",
    }
)
_ARTICLE_ANNOTATION_METHODS = frozenset({"get_article_annotations"})
_CASE_METHODS = frozenset(
    {
        "get_cjeu_judgments",
        "get_national_decisions",
        "get_preliminary_questions",
        "new_case_law",
        "new_preliminary_questions",
    }
)
_DOSSIER_METHODS = frozenset({"get_dossier"})
_NIM_METHODS = frozenset({"get_nims", "new_nims"})
_LOOKUP_CONCEPT_METHODS = frozenset({"get_eurovoc", "find_eurovoc_concept"})
_SUBJECT_METHODS = frozenset({"get_subject_matter", "get_directory_codes"})
_EXPRESSION_METHODS = frozenset({"get_expressions"})
_ACT_SEARCH_METHODS = frozenset(
    {
        "search_by_eurovoc",
        "search_by_subject_matter",
        "search_by_title",
        "search_communications",
        "new_by_eurovoc",
    }
)


def _return_contract_for_method(method_name: str) -> ReturnContract:
    if method_name == "resolve_celex":
        return ReturnContract(ActRef)
    if method_name == "get_act":
        return ReturnContract(ActDetail)
    if method_name in {"get_text", "get_summary"}:
        return ReturnContract(DocumentPayload)
    if method_name in _RELATION_METHODS:
        return ReturnContract(ListResult, item_type=RelationItem, query_name=method_name)
    if method_name in _ARTICLE_ANNOTATION_METHODS:
        return ReturnContract(ListResult, item_type=ArticleAnnotationItem, query_name=method_name)
    if method_name in _CASE_METHODS:
        return ReturnContract(ListResult, item_type=CaseLawItem, query_name=method_name)
    if method_name in _DOSSIER_METHODS:
        return ReturnContract(ListResult, item_type=DossierItem, query_name=method_name)
    if method_name in _NIM_METHODS:
        return ReturnContract(ListResult, item_type=NIMItem, query_name=method_name)
    if method_name in _LOOKUP_CONCEPT_METHODS:
        return ReturnContract(ListResult, item_type=EurovocTag, query_name=method_name)
    if method_name in _SUBJECT_METHODS:
        return ReturnContract(ListResult, item_type=SubjectMatterTag, query_name=method_name)
    if method_name in _EXPRESSION_METHODS:
        return ReturnContract(ListResult, item_type=ExpressionItem, query_name=method_name)
    if method_name in _ACT_SEARCH_METHODS:
        return ReturnContract(ListResult, item_type=ActRef, query_name=method_name)
    raise ValueError(f"Missing return contract for method: {method_name}")


RETURN_CONTRACTS: dict[str, ReturnContract] = {
    spec.method: _return_contract_for_method(spec.method) for spec in COMMANDS
}


def validate_command_specs(command_specs: list[CommandSpec] = COMMANDS) -> None:
    full_names = [spec.full_name for spec in command_specs]
    if len(full_names) != len(set(full_names)):
        raise ValueError("Command full names must be unique")

    methods = [spec.method for spec in command_specs]
    if len(methods) != len(set(methods)):
        raise ValueError("Command methods must be unique")

    for spec in command_specs:
        if spec.requires_since and spec.has_since:
            raise ValueError(f"{spec.full_name} cannot both require and optionally allow since")
        if spec.list_arg_name is not None and spec.scalar_arg_name is not None:
            raise ValueError(f"{spec.full_name} cannot require both list and scalar custom args")
        if spec.method not in RETURN_CONTRACTS:
            raise ValueError(f"{spec.full_name} has no return contract")


validate_command_specs()

__all__ = [
    "COMMANDS",
    "CommandParameterSpec",
    "CommandSpec",
    "RETURN_CONTRACTS",
    "ReturnContract",
    "validate_command_specs",
]
