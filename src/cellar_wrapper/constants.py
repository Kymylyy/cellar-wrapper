"""Project-wide constants."""

from __future__ import annotations

DEFAULT_SPARQL_ENDPOINT = "https://publications.europa.eu/webapi/rdf/sparql"
DEFAULT_RESOURCE_BASE_URL = "https://publications.europa.eu/resource"
DEFAULT_LANGUAGE = "eng"

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

SPARQL_PREFIXES = """
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
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
    "amends": "cdm:resource_legal_amends_resource_legal",
    "repeals": "cdm:resource_legal_repeals_resource_legal",
    "implicitly_repeals": "cdm:resource_legal_implicitly_repeals_resource_legal",
    "cites": "cdm:work_cites_work",
    "based_on": "cdm:resource_legal_based_on_resource_legal",
    "completes": "cdm:resource_legal_completes_resource_legal",
    "proposes_to_amend": "cdm:resource_legal_proposes_to_amend_resource_legal",
    "adopts": "cdm:resource_legal_adopts_resource_legal",
    "related": "cdm:work_related_to_work",
    "suspends": "cdm:resource_legal_suspends_resource_legal",
    "partially_suspends": "cdm:resource_legal_partially_suspends_resource_legal",
    "defers_application": "cdm:resource_legal_defers_application_of_resource_legal",
    "renders_obsolete": "cdm:resource_legal_renders_obsolete_resource_legal",
    "influences": "cdm:resource_legal_influences_resource_legal",
    "consolidates": "cdm:act_consolidated_consolidates_resource_legal",
    "corrects": "cdm:resource_legal_corrects_resource_legal",
    "nims": "cdm:measure_national_implementing_implements_resource_legal",
    "cjeu_interprets": "cdm:case-law_interpretes_resource_legal",
    "preliminary_questions": "cdm:communication_case_new_submits_preliminary_question_resource_legal",
}
