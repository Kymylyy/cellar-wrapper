"""SPARQL builders for download-related resolution."""

from __future__ import annotations

from cellar_wrapper.constants import PREDICATES

from .common import with_prefixes


def build_summary_lookup_query(work_uri: str) -> str:
    """Build query resolving legissum summary URI for a work URI."""
    query = f"""
SELECT DISTINCT ?summary WHERE {{
  {{ ?summary {PREDICATES["summary_summarizes_work"]} <{work_uri}> . }}
  UNION
  {{ ?summary {PREDICATES["summary_legislation_summarizes_resource_legal"]} <{work_uri}> . }}
}}
LIMIT 1
"""
    return with_prefixes(query)
