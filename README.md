# cellar-wrapper

Typed, sync-first Python wrapper for EU Publications Office CELLAR.

## Features
- `CellarClient` with full method surface from wrapper blueprint.
- Fail-fast error model with domain exceptions.
- JSON-first CLI (`cellar`) with command groups mirroring API areas.
- Stateless monitoring methods (`new_*`) with explicit `since`.

## Installation

```bash
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
```

All CLI responses are JSON:

```json
{"ok": true, "data": {...}}
```

Errors:

```json
{"ok": false, "error": {"type": "CellarValidationError", "message": "...", "details": {...}}}
```

## Development checks

```bash
ruff check
mypy
pytest
```

## Notes
- Default language: `eng`.
- Monitoring semantics: `date > since`.
- SPARQL transport is `POST`-first with automatic `GET` fallback for unsupported endpoints.
- `get_summary` enforces `Accept: application/xhtml+xml;type=xhtml5`.
- Search methods validate non-empty list inputs (`tags`, `codes`).
- Use one `CellarClient` instance per thread when doing concurrent work.
- Out of scope: ESA soft-law sources (EBA/ESMA/EIOPA websites/APIs).
