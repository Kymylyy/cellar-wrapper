"""SPARQL builders for download-related resolution."""

from __future__ import annotations

from cellar_wrapper.constants import PREDICATES

from .common import safe_iri, with_prefixes


def build_summary_lookup_query(work_uri: str) -> str:
    """Build query resolving legissum summary URI for a work URI."""
    work_iri = safe_iri(work_uri, field="work_uri")
    query = f"""
SELECT DISTINCT ?uri WHERE {{
  {{ ?uri {PREDICATES["summary_summarizes_work"]} <{work_iri}> . }}
  UNION
  {{ ?uri {PREDICATES["summary_legislation_summarizes_resource_legal"]} <{work_iri}> . }}
}}
LIMIT 1
"""
    return with_prefixes(query)
