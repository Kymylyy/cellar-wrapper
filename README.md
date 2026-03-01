# cellar-wrapper

[![CI](https://github.com/Kymylyy/cellar-wrapper/actions/workflows/ci.yml/badge.svg)](https://github.com/Kymylyy/cellar-wrapper/actions/workflows/ci.yml)

Typed, sync-first Python wrapper for EU Publications Office CELLAR, focused on
predictable contracts for legal and compliance data workflows.

## Repository overview
- `src/cellar_wrapper`: core package (`CellarClient`, typed models, SPARQL builders, CLI, MCP server entrypoint).
- `tests`: unit and integration tests.
- `docs`: API contract, blueprint, and research notes.

## Features
- `CellarClient` with full method surface from wrapper blueprint.
- Fail-fast error model with domain exceptions.
- JSON-first CLI (`cellar`) with command groups mirroring API areas.
- Optional MCP server (`cellar-mcp`) with tools generated 1:1 from `CommandSpec`.
- Stateless monitoring methods (`new_*`) with explicit `since`.
- Enriched metadata for `get_act`, `get_dossier`, and `get_nims`.
- Country-aware case-law support (`get_national_decisions(..., country="DEU")`).
- Local packaged EuroVoc index for `find_eurovoc_concept`, `search_by_eurovoc`, and `new_by_eurovoc`.
- Local packaged subject-matter index for `search_by_subject_matter`.

## Installation

```bash
# library + CLI
pip install cellar-wrapper

# library + CLI + MCP server
pip install "cellar-wrapper[mcp]"

# local development
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Quick start (Python)

```python
from cellar_wrapper import CellarClient

with CellarClient() as client:
    act = client.get_act("32022R2554")
    print(act.celex, act.title)

    amendments = client.get_amendments("32022R2554", limit=50)
    print(amendments.returned_count)

    new_citations = client.new_citations("32022R2554", since="2025-01-01")
    print(new_citations.returned_count)
```

## Quick start (CLI)

```bash
cellar lookup resolve-celex --celex 32022R2554
cellar relations get-amendments --celex 32022R2554 --limit 50
cellar monitoring new-citations --celex 32022R2554 --since 2025-01-01
cellar download get-text --celex 32022R2554 --lang eng --format pdf
cellar --user-agent "my-team-cellar-bot/1.0" lookup resolve-celex --celex 32022R2554
```

CLI success envelope:

```json
{"ok": true, "data": {...}}
```

CLI error envelope:

```json
{"ok": false, "error": {"type": "CellarValidationError", "message": "...", "details": {...}}}
```

`error.details` is always present in CLI output and can be an empty object (`{}`).

## Quick start (MCP)

```bash
# 1) register MCP server in Claude Code (one-time)
claude mcp add cellar -- cellar-mcp

# 2) optional runtime overrides (set before starting the MCP process)
export CELLAR_MCP_USER_AGENT="my-team-cellar-mcp/1.0"
export CELLAR_MCP_RETRIES=5

# 3) optional manual run for local debugging (stdio, foreground process)
cellar-mcp
```

Environment variables accepted by `cellar-mcp`:
- `CELLAR_MCP_BASE_URL_SPARQL`
- `CELLAR_MCP_BASE_URL_RESOURCE`
- `CELLAR_MCP_USER_AGENT`
- `CELLAR_MCP_RETRIES`
- `CELLAR_MCP_TIMEOUT_CONNECT`
- `CELLAR_MCP_TIMEOUT_READ`
- `CELLAR_MCP_TIMEOUT_WRITE`
- `CELLAR_MCP_TIMEOUT_POOL`

MCP env validation (startup fail-fast):
- if set, values cannot be empty/whitespace-only.
- `CELLAR_MCP_BASE_URL_SPARQL` / `CELLAR_MCP_BASE_URL_RESOURCE`: valid `http|https` URL.
- `CELLAR_MCP_RETRIES`: integer `>= 1`.
- `CELLAR_MCP_TIMEOUT_*`: float `> 0`.
- invalid config stops process before serving tools (`Invalid MCP configuration: ...`).

MCP tool payload contract:
- success returns raw method payload (for example `ListResult`, `ActDetail`, `DocumentPayload`) without CLI envelope (`ok/data`).
- domain errors are returned as MCP `ToolError` message:
  - `<CellarErrorType>: <message>`
  - optional suffix ` | details=<json>` appears only when details are non-empty.

## Development checks

```bash
ruff check
mypy
pytest
```

## Runtime taxonomy index refresh

Runtime EuroVoc resolve uses packaged file `src/cellar_wrapper/data/eurovoc_index.json`.
Refresh it from `docs/eurovoc_all.json` with:

```bash
python3 scripts/build_runtime_eurovoc_index.py
```

Runtime subject-matter resolve uses packaged file
`src/cellar_wrapper/data/subject_matter_index.json`.
Refresh it from `docs/subject_matter_all.json` with:

```bash
python3 scripts/build_runtime_subject_matter_index.py
```

## Manual contract test reports

Run manual checks for all public methods and generate JSON + HTML report:

```bash
PYTHONPATH=src python3 scripts/manual_test_contracts.py --workers 8 --runs 2
```

Default output location:
- `docs/manual_test/<YYYYMMDD_HHMMSS>/contract_methods_manual_test_report.json`
- `docs/manual_test/<YYYYMMDD_HHMMSS>/contract_methods_manual_test_report.html`

Report behavior:
- kwargs profiles are loaded from `docs/manual_test/kwargs_profiles.json`.
- profile list currently contains `7` profiles (`profile_a` ... `profile_g`).
- attempts cycle through profiles in order (`attempt 1 -> profile_a`, `attempt 2 -> profile_b`, ...).
- HTML shows kwargs and output inline (no expandable sections).

Render HTML for an existing report JSON:

```bash
PYTHONPATH=src python3 scripts/manual_test_contracts.py --from-json docs/manual_test/<RUN_ID>/contract_methods_manual_test_report.json
```

## Documentation map
- Docs index (start here): [docs/README.md](docs/README.md)
- API contract: [docs/API_CONTRACT.md](docs/API_CONTRACT.md)
- Method mapping: [docs/METHOD_MAPPING.md](docs/METHOD_MAPPING.md)
- Data artifacts inventory: [docs/DATA_ARTIFACTS.md](docs/DATA_ARTIFACTS.md)
- Wrapper blueprint (deprecated, historical): [docs/WRAPPER_BLUEPRINT.md](docs/WRAPPER_BLUEPRINT.md)
- Research notes archive: [docs/research/README.md](docs/research/README.md)
- EuroVoc performance notes: [docs/EUROVOC.md](docs/EUROVOC.md)

## Notes
- Default language: `eng`.
- `since` semantics:
  - non-monitoring methods (`search_*`, `get_*` with optional `since`): keep undated rows.
  - monitoring methods (`new_*`): strict `BOUND(date) && date > since`.
- Additional monitoring methods: `new_repeals`, `new_proposals_to_amend`, `new_preliminary_questions`.
- SPARQL transport is `POST`-first with automatic `GET` fallback for unsupported endpoints.
- GET fallback is skipped when encoded URL would exceed a safe length guard.
- HTTP retries respect `Retry-After` both on intermediate and final `429` responses.
- `get_summary` enforces `Accept: application/xhtml+xml;type=xhtml5`.
- Search methods validate non-empty list inputs (`tags`, `codes`).
- Downloads are streamed with a default max payload of `25MB` (configurable via `max_download_bytes`).
- Use one `CellarClient` instance per thread when doing concurrent work; do not share a single instance
  across threads because it wraps one shared `httpx.Client`.
- Out of scope: ESA soft-law sources (EBA/ESMA/EIOPA websites/APIs).
