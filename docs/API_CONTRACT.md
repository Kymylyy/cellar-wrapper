# CELLAR Wrapper API Contract

## Client constructor

```python
CellarClient(
  base_url_sparql: str = "https://publications.europa.eu/webapi/rdf/sparql",
  base_url_resource: str = "https://publications.europa.eu/resource",
  timeout: TimeoutConfig | None = None,
  retries: int = 3,  # must be >= 1
  max_download_bytes: int = 25 * 1024 * 1024,  # must be >= 1
  user_agent: str = "cellar-wrapper/0.1.0",
)
```

Transport constructor follows the same core knobs:

```python
HttpTransport(
  sparql_endpoint: str = "https://publications.europa.eu/webapi/rdf/sparql",
  retries: int = 3,
  max_download_bytes: int = 25 * 1024 * 1024,
  timeout: TimeoutConfig | None = None,
  user_agent: str = "cellar-wrapper/0.1.0",
)
```

## Input contract
- `celex: str` -> normalized to uppercase, validated against `^[0-9A-Z()_\-]{5,40}$`.
- `since: date | datetime | str` -> ISO-8601 parseable, normalized to `xsd:dateTime` in SPARQL:
  - date input -> `YYYY-MM-DDT00:00:00Z`
  - datetime input -> canonical ISO datetime (UTC-normalized)
- `lang: str` -> ISO 639-3 (`[a-zA-Z]{3}`), normalized to lowercase.
- `format: "pdf" | "xhtml" | "xml" | "rdf" | "docx"` for `get_text`.
- `limit: int` default `200`, max `1000`.
- `offset: int` default `0`.
- endpoint URLs (`base_url_sparql`, `base_url_resource`) must be valid `http|https` URLs.
- timeout fields (`connect/read/write/pool`) must be `> 0`.

## Output contract
- `QueryMeta(query_name, endpoint, executed_at, limit, offset)`
- `ListResult[T](items, returned_count, meta)`
- `ActRef`, `ActDetail`, `RelationItem`, `CaseLawItem`, `EurovocTag`, `SubjectMatterTag`, `ExpressionItem`, `DocumentPayload`
- Date-like model fields (`ActRef.date`, `ActDetail.date_*`) are parsed into typed `date | datetime`.

`RelationItem` may include article-level annotation fields for `get_article_annotations`:
- `annotation_uri`
- `annotation_article`
- `annotation_paragraph`
- `annotation_subparagraph`
- `annotation_point`
- `annotation_comment_on_legal_basis`

`DocumentPayload` returns base64-encoded content (`content_base64`).

## Empty result policy
- Collections return `ListResult(items=[])`.
- Missing CELEX/work raises `CellarNotFoundError`.

## Error contract
- `CellarError` (base)
- `CellarValidationError`
- `CellarHTTPError`
- `CellarTimeoutError`
- `CellarRateLimitError`
- `CellarSPARQLError`
- `CellarParseError`
- `CellarInternalError` (CLI catch-all for unexpected exceptions)
- `CellarNotFoundError`

`CellarSPARQLError` carries context fields (`query`, `response_excerpt`) for diagnostics.
`CellarParseError` carries structured `details` (`parser`, `row_index`, `field`, `value_excerpt`).

## HTTP behavior
- SPARQL queries are sent with `POST` (`application/x-www-form-urlencoded`) by default.
- Transport falls back to `GET` for SPARQL when `POST` is not supported (`405`, `415`, `501`).
- Retry status codes: `429, 502, 503, 504`.
- Attempts: `3` total.
- Backoff: exponential full-jitter (`uniform(0, cap)`), capped per-attempt.
- Default timeout: connect `10s`, read `30s`, write `30s`, pool `30s`.
- `Retry-After` is parsed to seconds when available on `429` (also for intermediate retries).

## Search input validation
- `search_by_eurovoc(tags=...)` requires at least one non-empty tag.
- `search_by_subject_matter(codes=...)` requires at least one non-empty code.

## CELEX resolution behavior
1. Exact match query (`=`).
2. Fallback query using `CONTAINS` token (CELEX without leading sector digit).
3. Fallback result must still contain an exact CELEX match; otherwise `CellarNotFoundError`.

## Summary download behavior
`get_summary` enforces:
- `Accept: application/xhtml+xml;type=xhtml5`
- `Accept-Language: <lang>`

## Download content-type validation
- `get_text` / `get_summary` validate response `Content-Type` compatibility with requested format.
- Generic `application/octet-stream` is accepted as fallback.
- Downloads are streamed and aborted when payload exceeds `max_download_bytes` (default `25MB`).

## CLI `--since`
- `--since` is available only for commands whose API methods support it.
- Commands like `get-deadlines` and `get-article-annotations` do not accept `--since`.

## `since` filtering semantics
- Non-monitoring methods with optional `since` (`search_*`, `get_*`) use:
  - `FILTER(!BOUND(?date) || ?date > since_datetime)`
- Monitoring methods (`new_*`) use strict date-bound:
  - `FILTER(BOUND(?date) && ?date > since_datetime)`

## Thread safety
- `CellarClient` is not safe for shared multi-thread use because one instance wraps one `httpx.Client`.
- Use one `CellarClient` instance per thread.

## Public methods

### LOOKUP
- `resolve_celex`
- `get_act`
- `get_eurovoc`
- `get_subject_matter`
- `get_legal_basis`
- `get_directory_codes`
- `get_expressions`

### RELATIONS
- `get_amendments`
- `get_repeals`
- `get_citations`
- `get_delegated_acts`
- `get_completing_acts`
- `get_proposals_to_amend`
- `get_adopted_act`
- `get_related_works`
- `get_other_relations`

### LIFECYCLE
- `get_consolidated_versions`
- `get_corrigenda`
- `get_nims`
- `get_dossier`
- `get_opinions`
- `get_deadlines`

### CASE LAW
- `get_cjeu_judgments`
- `get_ag_opinions`
- `get_preliminary_questions`
- `get_national_decisions`
- `get_article_annotations`

### SEARCH
- `search_by_eurovoc`
- `search_by_subject_matter`
- `search_by_title`
- `search_communications`
- `find_eurovoc_concept`

### MONITORING
- `new_citations`
- `new_amendments`
- `new_delegated_acts`
- `new_case_law`
- `new_corrigenda`
- `new_consolidated`
- `new_nims`
- `new_by_eurovoc`

### DOWNLOAD
- `get_text`
- `get_summary`
