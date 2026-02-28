"""Relation method specifications for generic relation dispatcher."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from cellar_wrapper.constants import PREDICATES
from cellar_wrapper.sparql import PredicateSpec


@dataclass(frozen=True)
class RelationCallSpec:
    """Mapping metadata for one relation-style public method."""

    predicates: Sequence[PredicateSpec]
    direction: str
    default_resource_type: str | None = None
    case_law: bool = False


RELATION_CALL_SPECS: dict[str, RelationCallSpec] = {
    "get_amendments": RelationCallSpec([PredicateSpec(PREDICATES["amends"], "amends")], "both"),
    "get_repeals": RelationCallSpec(
        [
            PredicateSpec(PREDICATES["repeals"], "repeals"),
            PredicateSpec(PREDICATES["implicitly_repeals"], "implicitly_repeals"),
        ],
        "both",
    ),
    "get_citations": RelationCallSpec([PredicateSpec(PREDICATES["cites"], "cites")], "both"),
    "get_delegated_acts": RelationCallSpec(
        [PredicateSpec(PREDICATES["based_on"], "based_on")],
        "incoming",
    ),
    "get_completing_acts": RelationCallSpec(
        [PredicateSpec(PREDICATES["completes"], "completes")],
        "incoming",
    ),
    "get_proposals_to_amend": RelationCallSpec(
        [PredicateSpec(PREDICATES["proposes_to_amend"], "proposes_to_amend")],
        "incoming",
    ),
    "get_adopted_act": RelationCallSpec([PredicateSpec(PREDICATES["adopts"], "adopts")], "incoming"),
    "get_related_works": RelationCallSpec([PredicateSpec(PREDICATES["related"], "related")], "both"),
    "get_other_relations": RelationCallSpec(
        [
            PredicateSpec(PREDICATES["suspends"], "suspends"),
            PredicateSpec(PREDICATES["partially_suspends"], "partially_suspends"),
            PredicateSpec(PREDICATES["defers_application"], "defers_application"),
            PredicateSpec(PREDICATES["renders_obsolete"], "renders_obsolete"),
            PredicateSpec(PREDICATES["influences"], "influences"),
        ],
        "both",
    ),
    "get_consolidated_versions": RelationCallSpec(
        [PredicateSpec(PREDICATES["consolidates"], "consolidates")],
        "incoming",
        default_resource_type="CONS_TEXT",
    ),
    "get_corrigenda": RelationCallSpec(
        [PredicateSpec(PREDICATES["corrects"], "corrects")],
        "incoming",
    ),
    "get_nims": RelationCallSpec(
        [PredicateSpec(PREDICATES["nims"], "nims")],
        "incoming",
        default_resource_type="MEAS_NATION_IMPL",
    ),
    "get_opinions": RelationCallSpec(
        [
            PredicateSpec(PREDICATES["contains_eesc_opinion"], "eesc_opinion"),
            PredicateSpec(PREDICATES["contains_ep_opinion"], "ep_opinion"),
            PredicateSpec(PREDICATES["influences"], "influences"),
        ],
        "incoming",
    ),
    "get_cjeu_judgments": RelationCallSpec(
        [PredicateSpec(PREDICATES["cjeu_interprets"], "cjeu_interprets")],
        "incoming",
        default_resource_type="JUDG",
        case_law=True,
    ),
    "get_preliminary_questions": RelationCallSpec(
        [PredicateSpec(PREDICATES["preliminary_questions"], "preliminary_questions")],
        "incoming",
        case_law=True,
    ),
    "new_citations": RelationCallSpec([PredicateSpec(PREDICATES["cites"], "cites")], "incoming"),
    "new_amendments": RelationCallSpec([PredicateSpec(PREDICATES["amends"], "amends")], "incoming"),
    "new_repeals": RelationCallSpec(
        [
            PredicateSpec(PREDICATES["repeals"], "repeals"),
            PredicateSpec(PREDICATES["implicitly_repeals"], "implicitly_repeals"),
        ],
        "incoming",
    ),
    "new_proposals_to_amend": RelationCallSpec(
        [PredicateSpec(PREDICATES["proposes_to_amend"], "proposes_to_amend")],
        "incoming",
    ),
    "new_delegated_acts": RelationCallSpec(
        [PredicateSpec(PREDICATES["based_on"], "based_on")],
        "incoming",
    ),
    "new_case_law": RelationCallSpec(
        [PredicateSpec(PREDICATES["cjeu_interprets"], "cjeu_interprets")],
        "incoming",
        default_resource_type="JUDG",
        case_law=True,
    ),
    "new_corrigenda": RelationCallSpec(
        [PredicateSpec(PREDICATES["corrects"], "corrects")],
        "incoming",
    ),
    "new_consolidated": RelationCallSpec(
        [PredicateSpec(PREDICATES["consolidates"], "consolidates")],
        "incoming",
        default_resource_type="CONS_TEXT",
    ),
    "new_nims": RelationCallSpec(
        [PredicateSpec(PREDICATES["nims"], "nims")],
        "incoming",
        default_resource_type="MEAS_NATION_IMPL",
    ),
    "new_preliminary_questions": RelationCallSpec(
        [PredicateSpec(PREDICATES["preliminary_questions"], "preliminary_questions")],
        "incoming",
        case_law=True,
    ),
}
