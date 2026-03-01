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
- `country: str` -> ISO 3166-1 alpha-3 (`[A-Z]{3}`), normalized to uppercase (for `get_national_decisions`).
- `format: "pdf" | "xhtml" | "xml" | "rdf" | "docx"` for `get_text`.
- `limit: int` default `200`, max `1000`.
- `offset: int` default `0`.
- endpoint URLs (`base_url_sparql`, `base_url_resource`) must be valid `http|https` URLs.
- timeout fields (`connect/read/write/pool`) must be `> 0`.

## Output contract
- `QueryMeta(query_name, endpoint, executed_at, limit, offset)`
- `ListResult[T](items, returned_count, meta)`
- `ActRef`, `ActDetail`, `RelationItem`, `DossierItem`, `NIMItem`, `CaseLawItem`, `EurovocTag`, `SubjectMatterTag`, `ExpressionItem`, `DocumentPayload`
- Date-like model fields (`ActRef.date`, `ActDetail.date_*`) are parsed into typed `date | datetime`.
- Collection payload invariant: `returned_count == len(items)` (including empty collections).

`ActDetail` exposes enriched metadata:
- `created_by_agents`
- `responsible_agents`
- `eea_relevant`
- `addresses_institutions`
- `signatory_names`

`CaseLawItem` may include `origin_country`.
`NIMItem` may include `implemented_by_country`.
`DossierItem` may include procedure metadata and status flags (`procedure_code`, `procedure_type`, `status_*`, `produces_act_*`).

`RelationItem` may include article-level annotation fields for `get_article_annotations`:
- `annotation_uri`
- `annotation_article`
- `annotation_paragraph`
- `annotation_subparagraph`
- `annotation_point`
- `annotation_comment_on_legal_basis`

`DocumentPayload` returns base64-encoded content (`content_base64`).

Method payload categories:
- collection methods return `ListResult[T]`.
- single-record metadata methods return typed models (`ActRef` / `ActDetail`).
- download methods return `DocumentPayload`.

## Empty result policy
- Collections return `ListResult(items=[])` when query matches no rows.
- Methods that resolve CELEX/work URI raise `CellarNotFoundError` when CELEX/work is missing (for example `resolve_celex`, `get_act`, and methods using `_resolve_work_uri`).
- `get_national_decisions` does not resolve work URI; CELEX is used as a reference substring filter. No matches (including unknown CELEX values) return empty `ListResult`, not `CellarNotFoundError`.

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
`CellarNotFoundError` carries structured `details` (for example `entity`, `celex`, `phase`).
`details` is optional in practice (error object may expose an empty `{}` payload).

## CLI vs MCP payload envelope
- CLI success payload: `{"ok": true, "data": <jsonable-method-payload>}`
- CLI error payload: `{"ok": false, "error": {"type": "...", "message": "...", "details": {...}}}`
- CLI always includes `error.details` key, but it can be empty (`{}`).
- MCP success payload: raw method payload only (no `ok/data` envelope).
- MCP error payload: MCP `ToolError` string, format:
  - `<CellarErrorType>: <message>`
  - optional suffix ` | details=<json>` is present only when details are non-empty.

## HTTP behavior
- SPARQL queries are sent with `POST` (`application/x-www-form-urlencoded`) by default.
- Transport falls back to `GET` for SPARQL when `POST` is not supported (`405`, `415`, `501`).
- GET fallback is blocked when encoded URL length exceeds a safe guardrail.
- Retry status codes: `429, 502, 503, 504`.
- Attempts: `3` total.
- Backoff: exponential full-jitter (`uniform(0, cap)`), capped per-attempt.
- Default timeout: connect `10s`, read `30s`, write `30s`, pool `30s`.
- `Retry-After` is parsed to seconds when available on `429` (also for intermediate retries).
- Parsed `Retry-After` is clamped to `MAX_BACKOFF_SECONDS` before sleeping.

## Search input validation
- `search_by_eurovoc(tags=...)` requires at least one non-empty tag.
- `search_by_subject_matter(codes=...)` requires at least one non-empty code.

## EuroVoc execution model
- `search_by_eurovoc` and `new_by_eurovoc` run in two steps:
  1. resolve each tag via `find_eurovoc_concept`,
  2. final query by exact concept URIs with `VALUES ?concept`.
- Concept resolve remains language-scoped to label `LANG = 'en' || ''` (independent from `lang` argument used for title expression lookup).
- If no concept URI is resolved for provided tags, methods return an empty list result without executing the final work query.

## Dossier execution model
- `get_dossier` uses staged SPARQL execution to improve latency on larger dossiers:
  1. a core-relation step selects dossier links via `cdm:dossier_contains_work` and paginates that reduced set early,
  2. a metadata enrichment step resolves optional procedure/status and work metadata (`cdm:procedure_code_interinstitutional_reference_procedure`, `cdm:procedure_code_interinstitutional_has_type`, `cdm:dossier_*`, `cdm:dossier_produces_resource_legal`, CELEX/title/date/type).
- Result ordering is deterministic for pagination: primary sort by `date`, secondary tie-break by resource key (`other` work URI).

## CELEX resolution behavior
1. Exact match query (`=`).
2. Fallback query using `CONTAINS` token (CELEX without leading sector digit).
3. Fallback result must still contain an exact CELEX match; otherwise `CellarNotFoundError`.

## Summary download behavior
`get_summary` enforces:
- `Accept: application/xhtml+xml;type=xhtml5`
- `Accept-Language: <lang>`
- Download `404` is mapped to `CellarNotFoundError` with `details.entity = "summary"`.

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

## MCP contract
- Entrypoint: `cellar-mcp` (`cellar_wrapper.mcp_server:main`).
- Transport: stdio only.
- Tool surface: generated from `CommandSpec` and `COMMANDS`; currently `45` tools.
- Tool names match CLI command slugs exactly (for example `resolve-celex`, `get-amendments`, `new-citations`).
- Tool argument mapping reuses `build_method_kwargs`:
  - `requires_celex` -> required `celex`
  - `requires_since` -> required `since`
  - `has_since` -> optional `since`
  - `has_resource_type` -> optional `resource_type`
  - `has_country` -> optional `country`
  - `has_lang` -> optional `lang` default `eng`
  - `has_limit_offset` -> optional `limit` default `200`, `offset` default `0`
  - `has_format` -> optional `format` default `pdf`
  - `list_arg_name` -> required `list[str]` argument
  - `scalar_arg_name` -> required `str` argument
- Result payload:
  - success returns the method payload directly (JSON-serializable object), not CLI-style `{ok: true}` envelope.
  - wrapper `CellarError` exceptions are raised as MCP tool errors with message format:
    - `<CellarErrorType>: <message>`
    - optional ` | details=<json>` suffix only when details are non-empty.
  - unexpected runtime exceptions are mapped to `CellarInternalError` with `details.original_type`.
- Runtime configuration for `cellar-mcp` uses environment variables:
  - `CELLAR_MCP_BASE_URL_SPARQL`
  - `CELLAR_MCP_BASE_URL_RESOURCE`
  - `CELLAR_MCP_USER_AGENT`
  - `CELLAR_MCP_RETRIES`
  - `CELLAR_MCP_TIMEOUT_CONNECT`
  - `CELLAR_MCP_TIMEOUT_READ`
  - `CELLAR_MCP_TIMEOUT_WRITE`
  - `CELLAR_MCP_TIMEOUT_POOL`
- Environment validation rules (fail-fast on startup):
  - all env vars above are optional, but if set they cannot be empty/whitespace-only.
  - `CELLAR_MCP_BASE_URL_SPARQL`, `CELLAR_MCP_BASE_URL_RESOURCE`: must be valid `http|https` URLs.
  - `CELLAR_MCP_USER_AGENT`: non-empty string.
  - `CELLAR_MCP_RETRIES`: integer, then validated as `>= 1`.
  - `CELLAR_MCP_TIMEOUT_CONNECT`, `CELLAR_MCP_TIMEOUT_READ`, `CELLAR_MCP_TIMEOUT_WRITE`, `CELLAR_MCP_TIMEOUT_POOL`: float, then validated as `> 0`.
  - invalid env configuration aborts startup before `server.run("stdio")` with `SystemExit("Invalid MCP configuration: ...")`.

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
- `new_repeals`
- `new_proposals_to_amend`
- `new_delegated_acts`
- `new_case_law`
- `new_preliminary_questions`
- `new_corrigenda`
- `new_consolidated`
- `new_nims`
- `new_by_eurovoc`

### DOWNLOAD
- `get_text`
- `get_summary`
