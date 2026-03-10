# cellar-wrapper

[![CI](https://github.com/Kymylyy/cellar-wrapper/actions/workflows/ci.yml/badge.svg)](https://github.com/Kymylyy/cellar-wrapper/actions/workflows/ci.yml)

Typed, sync-first Python wrapper for EU Publications Office CELLAR, focused on predictable contracts for legal and compliance data workflows.

This project is community-maintained and unofficial. It is not affiliated with, endorsed by, or operated by the European Union or the Publications Office of the European Union.

## Features

- Typed `CellarClient` covering lookup, search, lifecycle, relations, case-law, monitoring, and download methods.
- JSON-first CLI (`cellar`) with command groups that mirror API areas.
- Optional MCP server runtime (install `mcp` extra, run via module entrypoint).
- Fail-fast domain errors and stable JSON envelopes for CLI failures.
- Packaged runtime indexes for EuroVoc and subject-matter resolution.

## Installation

```bash
# library + CLI
pip install cellar-wrapper

# library + CLI + MCP runtime support
pip install "cellar-wrapper[mcp]"
```

## Quick Start (Python)

```python
from cellar_wrapper import CellarClient

with CellarClient() as client:
    act = client.get_act("32022R2554")
    print(act.celex, act.title)
```

## Quick Start (CLI)

```bash
cellar --version
cellar lookup resolve-celex --celex 32022R2554
cellar relations get-amendments --celex 32022R2554 --limit 50
cellar monitoring new-citations --celex 32022R2554 --since 2025-01-01
```

CLI success envelope:

```json
{"ok": true, "data": {...}}
```

CLI error envelope:

```json
{"ok": false, "error": {"type": "CellarValidationError", "message": "...", "details": {...}}}
```

## Quick Start (MCP)

Install with extra:

```bash
pip install "cellar-wrapper[mcp]"
```

Run server (stdio):

```bash
python -m cellar_wrapper.mcp_server
```

Version check:

```bash
python -m cellar_wrapper.mcp_server --version
```

MCP runtime environment variables:

- `CELLAR_MCP_BASE_URL_SPARQL`
- `CELLAR_MCP_BASE_URL_RESOURCE`
- `CELLAR_MCP_USER_AGENT`
- `CELLAR_MCP_RETRIES`
- `CELLAR_MCP_TIMEOUT_CONNECT`
- `CELLAR_MCP_TIMEOUT_READ`
- `CELLAR_MCP_TIMEOUT_WRITE`
- `CELLAR_MCP_TIMEOUT_POOL`

## Development

Required PR checks:

```bash
ruff check
mypy
pytest -m "not live"
python -m build --sdist --wheel
```

Optional checks:

- Live endpoint smoke test: `pytest -m live` with `CELLAR_LIVE=1`

## Runtime Data

Runtime resolve methods use packaged files:

- `src/cellar_wrapper/data/eurovoc_index.json`
- `src/cellar_wrapper/data/subject_matter_index.json`

Data sources, attribution, and artifact policy:

- https://github.com/Kymylyy/cellar-wrapper/blob/main/docs/DATA_PROVENANCE.md
- https://github.com/Kymylyy/cellar-wrapper/blob/main/docs/DATA_ARTIFACTS.md

## Documentation

- Docs index: https://github.com/Kymylyy/cellar-wrapper/blob/main/docs/README.md
- API contract: https://github.com/Kymylyy/cellar-wrapper/blob/main/docs/API_CONTRACT.md
- Command contracts: https://github.com/Kymylyy/cellar-wrapper/blob/main/docs/COMMAND_CONTRACTS.md
- Method mapping: https://github.com/Kymylyy/cellar-wrapper/blob/main/docs/METHOD_MAPPING.md
- Plain-language command guide: https://github.com/Kymylyy/cellar-wrapper/blob/main/docs/COMMANDS_SIMPLE.md

## Project Policies

- License: https://github.com/Kymylyy/cellar-wrapper/blob/main/LICENSE
- Contributing: https://github.com/Kymylyy/cellar-wrapper/blob/main/CONTRIBUTING.md
- Security: https://github.com/Kymylyy/cellar-wrapper/blob/main/SECURITY.md
- Support: https://github.com/Kymylyy/cellar-wrapper/blob/main/SUPPORT.md
- Code of Conduct: https://github.com/Kymylyy/cellar-wrapper/blob/main/CODE_OF_CONDUCT.md
