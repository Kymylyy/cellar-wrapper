"""Project-wide constants."""

from __future__ import annotations

from cellar_wrapper.version import __version__

DEFAULT_SPARQL_ENDPOINT = "https://publications.europa.eu/webapi/rdf/sparql"
DEFAULT_RESOURCE_BASE_URL = "https://publications.europa.eu/resource"
DEFAULT_LANGUAGE = "eng"
DEFAULT_USER_AGENT = f"cellar-wrapper/{__version__}"

DEFAULT_LIMIT = 200
MAX_LIMIT = 1000
DEFAULT_OFFSET = 0

DEFAULT_CONNECT_TIMEOUT = 10.0
DEFAULT_READ_TIMEOUT = 30.0
DEFAULT_WRITE_TIMEOUT = 30.0
DEFAULT_POOL_TIMEOUT = 30.0

DEFAULT_RETRIES = 3
RETRY_STATUS_CODES = frozenset({429, 502, 503, 504})
MAX_BACKOFF_SECONDS = 8.0
DEFAULT_MAX_DOWNLOAD_BYTES = 25 * 1024 * 1024
SPARQL_POST_FALLBACK_STATUS_CODES = frozenset({405, 415, 501})

SPARQL_PREFIXES = """
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
""".strip()

TEXT_FORMAT_ACCEPT: dict[str, str] = {
    "pdf": "application/pdf",
    "xhtml": "application/xhtml+xml",
    "xml": "application/xml",
    "rdf": "application/rdf+xml",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

SUMMARY_ACCEPT = "application/xhtml+xml;type=xhtml5"

LANGUAGE_URI_TEMPLATE = "http://publications.europa.eu/resource/authority/language/{lang}"

RESOURCE_TYPE_URI_TEMPLATE = "http://publications.europa.eu/resource/authority/resource-type/{resource_type}"

PREDICATES = {
    "resource_legal_id_celex": "cdm:resource_legal_id_celex",
    "resource_legal_eli": "cdm:resource_legal_eli",
    "work_has_resource_type": "cdm:work_has_resource-type",
    "resource_legal_in_force": "cdm:resource_legal_in-force",
    "resource_legal_eea": "cdm:resource_legal_eea",
    "work_date_document": "cdm:work_date_document",
    "resource_legal_date_end_of_validity": "cdm:resource_legal_date_end-of-validity",
    "work_created_by_agent": "cdm:work_created_by_agent",
    "resource_legal_responsibility_of_agent": "cdm:resource_legal_responsibility_of_agent",
    "resource_legal_addresses_institution": "cdm:resource_legal_addresses_institution",
    "resource_legal_signatory_name2": "cdm:resource_legal_signatory_name2",
    "expression_belongs_to_work": "cdm:expression_belongs_to_work",
    "expression_uses_language": "cdm:expression_uses_language",
    "expression_title": "cdm:expression_title",
    "resource_legal_service_responsible": "cdm:resource_legal_service_responsible",
    "case_law_ecli": "cdm:case-law_ecli",
    "case_law_delivered_by_court_formation": "cdm:case-law_delivered_by_court-formation",
    "case_law_delivered_by_advocate_general": "cdm:case-law_delivered_by_advocate-general",
    "case_law_originates_in_country": "cdm:case-law_originates_in_country",
    "work_is_about_concept_eurovoc": "cdm:work_is_about_concept_eurovoc",
    "subject_matter": "cdm:resource_legal_is_about_subject-matter",
    "directory_code": "cdm:resource_legal_is_about_concept_directory-code",
    "amends": "cdm:resource_legal_amends_resource_legal",
    "repeals": "cdm:resource_legal_repeals_resource_legal",
    "implicitly_repeals": "cdm:resource_legal_implicitly_repeals_resource_legal",
    "cites": "cdm:work_cites_work",
    "based_on": "cdm:resource_legal_based_on_resource_legal",
    "based_on_concept_treaty": "cdm:resource_legal_based_on_concept_treaty",
    "completes": "cdm:resource_legal_completes_resource_legal",
    "proposes_to_amend": "cdm:resource_legal_proposes_to_amend_resource_legal",
    "adopts": "cdm:resource_legal_adopts_resource_legal",
    "related": "cdm:work_related_to_work",
    "dossier_contains_work": "cdm:dossier_contains_work",
    "dossier_identifier": "cdm:dossier_identifier",
    "dossier_adopted_proposal": "cdm:dossier_adopted-proposal",
    "dossier_pending_proposal": "cdm:dossier_pending-proposal",
    "dossier_withdrawn_proposal": "cdm:dossier_withdrawn-proposal",
    "dossier_produces_resource_legal": "cdm:dossier_produces_resource_legal",
    "procedure_code_interinstitutional_reference_procedure": (
        "cdm:procedure_code_interinstitutional_reference_procedure"
    ),
    "procedure_code_interinstitutional_has_type": "cdm:procedure_code_interinstitutional_has_type",
    "contains_eesc_opinion": "cdm:resource_legal_contains_eesc_opinion_on_resource_legal",
    "contains_ep_opinion": "cdm:resource_legal_contains_ep_opinion_on_resource_legal",
    "suspends": "cdm:resource_legal_suspends_resource_legal",
    "partially_suspends": "cdm:resource_legal_partially_suspends_resource_legal",
    "defers_application": "cdm:resource_legal_defers_application_of_resource_legal",
    "renders_obsolete": "cdm:resource_legal_renders_obsolete_resource_legal",
    "influences": "cdm:resource_legal_influences_resource_legal",
    "deadline": "cdm:resource_legal_date_deadline",
    "entry_into_force": "cdm:resource_legal_date_entry-into-force",
    "directive_transposition": "cdm:directive_date_transposition",
    "consolidates": "cdm:act_consolidated_consolidates_resource_legal",
    "corrects": "cdm:resource_legal_corrects_resource_legal",
    "nims": "cdm:measure_national_implementing_implements_resource_legal",
    "implemented_by_country": "cdm:measure_national_implementing_implemented_by_country",
    "cjeu_interprets": "cdm:case-law_interpretes_resource_legal",
    "ag_opinion": "cdm:case-law_has_conclusions_opinion_advocate-general",
    "national_act_reference": "cdm:case-law_national_act_reference_european",
    "preliminary_questions": "cdm:communication_case_new_submits_preliminary_question_resource_legal",
    "summary_summarizes_work": "cdm:summary_summarizes_work",
    "summary_legislation_summarizes_resource_legal": "cdm:summary_legislation_eu_summarizes_resource_legal",
}
