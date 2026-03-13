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
- `to: date | datetime | str` -> same normalization rules as `since`; used as a strict upper bound in SPARQL.
- `lang: str` -> ISO 639-3 (`[a-zA-Z]{3}`), normalized to lowercase.
- `direction: "incoming" | "outgoing" | "both"` -> optional relation-direction filter for symmetric relation commands; default `both`.
- `country: str` -> ISO 3166-1 alpha-3 (`[A-Z]{3}`), normalized to uppercase (for `get_national_decisions`).
- `format: "pdf" | "xhtml" | "xml" | "rdf" | "docx"` for `get_text`.
- `limit: int` default `200`, max `1000`.
- `offset: int` default `0`.
- endpoint URLs (`base_url_sparql`, `base_url_resource`) must be valid `http|https` URLs.
- timeout fields (`connect/read/write/pool`) must be `> 0`.

## Output contract
- `QueryMeta(query_name, endpoint, executed_at, limit, offset)`
- `ListResult[T](items, returned_count, meta)`
- `ActRef`, `ActDetail`, `RelationItem`, `ArticleAnnotationItem`, `DossierItem`, `NIMItem`, `CaseLawItem`, `EurovocTag`, `SubjectMatterTag`, `ExpressionItem`, `DocumentPayload`
- Date-like model fields (`ActRef.date`, `ActDetail.date_*`) are parsed into typed `date | datetime`.
- Collection payload invariant: `returned_count == len(items)` (including empty collections).

`ActDetail` exposes enriched metadata:
- `created_by_agents`
- `responsible_agents`
- `eea_relevant`
- `addresses_institutions`
- `signatory_names`

Act-detail caveats:
- `addresses_institutions` is act-dependent and may legitimately be empty even when `created_by_agents` or `responsible_agents` are populated.
- For proposals, `date_end_of_validity = 9999-12-31` can appear as a placeholder max date rather than a meaningful end-of-validity signal.

`CaseLawItem` may include `origin_country`.
`NIMItem` may include `implemented_by_country`.
`DossierItem` may include procedure metadata and status flags (`procedure_code`, `procedure_type`, `status_*`, `produces_act_*`).

`RelationItem` is the generic legal-relation record. It includes shared relation fields such as:
- `direction`
- `predicate`
- `relation_type`

For relation semantics, note in particular:
- `get_based_on_acts` is backed by `cdm:resource_legal_based_on_resource_legal` and returns the broad incoming `based_on` bucket.
- `get_completing_acts` is backed by `cdm:resource_legal_completes_resource_legal` and is the narrower "supplements/completes this act" relation.
- For some acts, the two result sets can overlap substantially, but `get_completing_acts` is typically the narrower subset.
- `get_based_on_acts` can include non-delegated resource types such as implementing acts, drafts, reports, and resolutions.
- `get_corrigenda` and `new_corrigenda` default to `resource_type = CORRIGENDUM`, while still allowing an explicit override.
- When a relation-style command is filtered by `resource_type`, the returned `resource_type` field is constrained to the selected type rather than any sibling type attached to the same CELLAR work.
- `get_legal_basis` can mix treaty-basis rows, legal acts based on the act, and other based-on documents such as recommendations.
- `get_legal_basis` is also the correct reverse-lookup path for delegated act -> base act.
- `get_citations` is not limited to legal acts; depending on the act, it can include communications, impact assessments, staff working documents, and similar materials.
- For proposal acts, `get_amendments` and `get_repeals` may return empty `incoming`/`both` results even when the proposal text clearly indicates planned amendments or repeals. Treat this as a current CELLAR relation-data limitation for proposals.
- `get_other_relations` is a sparse catch-all bucket over predicates such as suspend/defer/obsolete/influence and is often empty for mainstream final acts.

`ArticleAnnotationItem` extends `RelationItem` and is returned by `get_article_annotations`. It may include:
- `annotation_uri`
- `annotation_article`
- `annotation_paragraph`
- `annotation_subparagraph`
- `annotation_point`
- `annotation_comment_on_legal_basis`

Normal relation-style commands no longer expose `annotation_*` fields in their payload shape.

`DocumentPayload` returns base64-encoded content (`content_base64`).

Method payload categories:
- collection methods return `ListResult[T]`.
- single-record metadata methods return typed models (`ActRef` / `ActDetail`).
- download methods return `DocumentPayload`.
- `find_eurovoc_concept` sets `meta.endpoint = "local://eurovoc-index"` (local packaged index).

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
For local index failures, details include `source = "local_eurovoc_index"` or
`source = "local_subject_matter_index"` plus phase metadata.
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
- `find_eurovoc_concept` resolves tags from a packaged local index (`src/cellar_wrapper/data/eurovoc_index.json`), not via live SPARQL.
- `search_by_eurovoc` and `new_by_eurovoc` run in two steps:
  1. resolve each tag against the local index,
  2. final live SPARQL query by exact concept URIs with `VALUES ?concept`.
- Local resolve keeps current business semantics: case-insensitive substring match on label (`CONTAINS`-style behavior).
- If no concept URI is resolved for provided tags, methods return an empty list result without executing the final work query.
- Local index load/parse failures are fail-fast (`CellarParseError`) and do not fall back to live resolve queries.

## Subject-matter execution model
- `search_by_subject_matter` resolves `codes` from a packaged local index (`src/cellar_wrapper/data/subject_matter_index.json`).
- Method runs in two steps:
  1. resolve provided `codes` against local index,
  2. final live SPARQL query by exact concept URIs with `VALUES ?concept`.
- Local resolve keeps current business semantics: case-insensitive substring match over concept URI and label (`CONTAINS`-style behavior).
- If no concept URI is resolved for provided `codes`, method returns an empty list result without executing the final work query.
- Local index load/parse failures are fail-fast (`CellarParseError`) and do not fall back to live resolve queries.

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

## CLI date bounds
- `--since` is available only for commands whose API methods support date filtering.
- `--to` is available on the same commands as `--since`.
- Monitoring commands keep required `--since`; `--to` is optional.
- Commands like `get-deadlines` and `get-article-annotations` accept neither `--since` nor `--to`.

## Contract migration note
- `get_article_annotations` is the only public command that returns `ArticleAnnotationItem`.
- Generic relation commands (`get_amendments`, `get_repeals`, `get_citations`, lifecycle relation methods, and relation-style monitoring methods) now return plain `RelationItem` rows without `annotation_*`.
- This is an intentional contract cleanup: `annotation_*` is specific to OWL article-annotation rows, not to ordinary relation rows.

## Date filtering semantics
- `since` is a strict lower bound: `?date > since_datetime`.
- `to` is a strict upper bound: `?date < to_datetime`.
- If both are supplied, the effective comparison is `?date > since_datetime && ?date < to_datetime`.
- Date-only inputs for both bounds normalize to `YYYY-MM-DDT00:00:00Z`.
- Inverted ranges (`since > to` after normalization) raise `CellarValidationError`.
- Non-monitoring methods with optional bounds (`search_*`, `get_*`) use:
  - `FILTER(!BOUND(?date) || comparison)`
- Monitoring methods (`new_*`) use strict dated-only bounds:
  - `FILTER(BOUND(?date) && comparison)`

## Thread safety
- `CellarClient` is not safe for shared multi-thread use because one instance wraps one `httpx.Client`.
- Use one `CellarClient` instance per thread.

## MCP contract
- Entrypoint: `python -m cellar_wrapper.mcp_server` (install extra: `pip install "cellar-wrapper[mcp]"`).
- Transport: stdio only.
- Tool surface: generated from `CommandSpec` and `COMMANDS`; currently `45` tools.
- Tool names match CLI command slugs exactly (for example `resolve-celex`, `get-amendments`, `new-citations`).
- Tool argument mapping reuses `build_method_kwargs`:
  - `requires_celex` -> required `celex`
  - `requires_since` -> required `since`
  - `has_since` -> optional `since`
  - commands with date filtering -> optional `to`
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
- Runtime configuration for MCP server uses environment variables:
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
See [COMMAND_CONTRACTS.md](COMMAND_CONTRACTS.md) for the canonical
command/method/return-model matrix derived from `COMMANDS` plus shared runtime
return contracts.
