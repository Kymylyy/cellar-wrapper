# Contributing

Thanks for contributing.

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Required Checks Before PR

```bash
ruff check
mypy
pytest -m "not live"
python -m build --sdist --wheel
```

## Optional Checks

- `pytest -m live` with `CELLAR_LIVE=1` for live endpoint validation.

## Scope and Contracts

- `docs/CONTRACT_REFERENCE.md` is the maintained behavior/source-of-truth document.
- `docs/examples/contract-examples.json` is a curated human-facing examples corpus, not the full command surface.
- `docs/CONTRACT_EXAMPLES.md` is generated from that curated JSON and must stay in sync when the curated examples change.
- Full command/contract coverage is tracked separately in `docs/artifact/command-manifest.json` and in tests.
- `docs/MAINTAINER_GUIDE.md` documents the refresh/audit workflow for examples and docs.
- Changes to behavior or CLI output must update docs in the same PR.
- Keep changes surgical; avoid unrelated refactors.

## Pull Requests

- Open small, focused PRs with clear intent.
- Include test coverage for bug fixes when practical.
- If something was skipped, state exactly what and why.
