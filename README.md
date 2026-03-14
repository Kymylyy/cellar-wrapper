# cellar-wrapper

[![CI](https://github.com/Kymylyy/cellar-wrapper/actions/workflows/ci.yml/badge.svg)](https://github.com/Kymylyy/cellar-wrapper/actions/workflows/ci.yml)

`cellar-wrapper` helps you get legal and legislative data from the EU Publications Office CELLAR service in a simpler, more practical way.

You can use it:

- as a Python library,
- from the command line,
- and, if needed, as an MCP server for AI/tool integrations.

This project is community-maintained and unofficial. It is not affiliated with, endorsed by, or operated by the European Union or the Publications Office of the European Union.

## Important status

This project is still being built.

The Python API, CLI commands, MCP interface, and response shapes may change. Do not treat the current interface as final or stable.

## What it is for

The project is meant for people who need to:

- look up an EU act by CELEX number,
- fetch basic metadata for an act,
- check relations such as amendments, repeals, citations, and related case law,
- monitor whether something new appeared after a given date,
- download text or legislative summaries,
- search acts by title, EuroVoc, or subject matter.

In short: it is a practical access layer over CELLAR for legal research, compliance work, and structured data collection.

## Current state and limitations

This is a hobby project, not an official product.

Before using it seriously, keep in mind:

- the project is still evolving, so commands and outputs may change,
- some data comes directly from CELLAR and can be incomplete, sparse, or inconsistent,
- not every legal question maps neatly to one command,
- MCP support exists, but the main practical use today is still Python and the CLI,

## Installation

Library and CLI:

```bash
pip install cellar-wrapper
```

Library, CLI, and MCP support:

```bash
pip install "cellar-wrapper[mcp]"
```

## Quick use from the command line

For most people, the CLI is the easiest way to start.

Check that the CLI is installed:

```bash
cellar --version
```

Resolve a CELEX number:

```bash
cellar lookup resolve-celex --celex 32022R2554
```

Get metadata for one act:

```bash
cellar lookup get-act --celex 32022R2554
```

Check amendments:

```bash
cellar relations get-amendments --celex 32022R2554 --limit 50
```

Check what is new since a date:

```bash
cellar monitoring new-citations --celex 32022R2554 --since 2025-01-01
```

The CLI returns JSON. On success:

```json
{"ok": true, "data": {...}}
```

On error:

```json
{"ok": false, "error": {"type": "CellarValidationError", "message": "...", "details": {...}}}
```

## Quick use from Python

```python
from cellar_wrapper import CellarClient

with CellarClient() as client:
    act = client.get_act("32022R2554")
    print(act.celex, act.title)
```

## Help, bugs, and security

If something does not work, or if you want to ask how to use the project:

- Support and usage questions: [SUPPORT.md](SUPPORT.md)
- Bug reports and feature requests: https://github.com/Kymylyy/cellar-wrapper/issues
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Security reporting: [SECURITY.md](SECURITY.md)

## Quick use as MCP

If you want to connect the project to an assistant or another tool through MCP, install the MCP extra:

```bash
pip install "cellar-wrapper[mcp]"
```

Run the server:

```bash
python -m cellar_wrapper.mcp_server
```

Check the version:

```bash
python -m cellar_wrapper.mcp_server --version
```

Environment variables supported by the MCP server:

- `CELLAR_MCP_BASE_URL_SPARQL`
- `CELLAR_MCP_BASE_URL_RESOURCE`
- `CELLAR_MCP_USER_AGENT`
- `CELLAR_MCP_RETRIES`
- `CELLAR_MCP_TIMEOUT_CONNECT`
- `CELLAR_MCP_TIMEOUT_READ`
- `CELLAR_MCP_TIMEOUT_WRITE`
- `CELLAR_MCP_TIMEOUT_POOL`

## Where to look next

- Docs index: https://github.com/Kymylyy/cellar-wrapper/blob/main/docs/README.md
- Command guide: https://github.com/Kymylyy/cellar-wrapper/blob/main/docs/COMMAND_GUIDE.md
- Curated examples: https://github.com/Kymylyy/cellar-wrapper/blob/main/docs/CONTRACT_EXAMPLES.md
- Contract reference: https://github.com/Kymylyy/cellar-wrapper/blob/main/docs/CONTRACT_REFERENCE.md

## For contributors

Main local checks:

```bash
ruff check
mypy
pytest -m "not live"
python -m build --sdist --wheel
```
