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
- Manual contract report generation documented in `docs/manual_test/README.md`.

## Scope and Contracts

- `docs/API_CONTRACT.md` is the behavior source-of-truth.
- Changes to behavior or CLI output must update docs in the same PR.
- Keep changes surgical; avoid unrelated refactors.

## Pull Requests

- Open small, focused PRs with clear intent.
- Include test coverage for bug fixes when practical.
- If something was skipped, state exactly what and why.
