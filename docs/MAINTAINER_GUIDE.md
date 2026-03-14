# Maintainer Guide

Use this guide when a contract change, payload change, or docs cleanup affects
public examples or maintained documentation.

## Canonical sources

- Command inventory, argument defaults, MCP schema shape, and return-contract mapping come from `src/cellar_wrapper/cli_specs.py`.
- Full command coverage is exported to `docs/artifact/command-manifest.json`.
- Curated examples live in `docs/examples/contract-examples.json`.
- [CONTRACT_EXAMPLES.md](CONTRACT_EXAMPLES.md) is generated from that JSON and must not be hand-edited.
- Curated examples are for humans. They are not required to cover every command.
- [CONTRACT_REFERENCE.md](CONTRACT_REFERENCE.md) is the maintained prose reference for envelopes, return types, caveats, and MCP behavior.

## Example refresh workflow

1. Run `python scripts/render_command_manifest.py` after command-surface changes so the full machine-readable coverage artifact stays current.
2. Update `docs/examples/contract-examples.json` only when you want to add or refresh curated human-facing examples for user-visible behavior.
3. Run `python scripts/render_contract_examples.py` to regenerate [CONTRACT_EXAMPLES.md](CONTRACT_EXAMPLES.md) when the curated example corpus changes.
4. Run `python scripts/audit_contract_examples_live.py` only when curated examples changed or when a user-visible contract/output change affects commands already documented there.
5. If the live audit reports differences, decide whether each difference is:
   - an intended behavior change that requires JSON/docs updates,
   - an upstream data drift that should be reflected in curated examples,
   - or a bug/regression that must be fixed before docs are refreshed.

## CI expectations

- Regular CI should always validate the command surface through tests and the generated command manifest artifact.
- The live examples audit is maintainer-oriented verification, not a default CI gate.
- If a change does not affect curated examples or user-visible docs output, it should usually require test updates only.

## Documentation update rules

- Keep [COMMAND_GUIDE.md](COMMAND_GUIDE.md) focused on what a command is for and when to use it.
- Keep [CONTRACT_REFERENCE.md](CONTRACT_REFERENCE.md) focused on maintained behavior, exact input/output shape, and caveats that remain true across examples.
- Keep research or one-off investigations in `docs/research/`; do not promote archival notes into active docs without re-checking them against current behavior and live payloads.
- If a contract caveat was discovered while curating examples, either encode it into example `purpose` text or promote it into [CONTRACT_REFERENCE.md](CONTRACT_REFERENCE.md). Do not create a second stand-alone notes file.

## Archive policy

- `docs/research/` remains available for historical context only.
- Research files may be older than current live payloads and should not be treated as maintained contract docs.
- Top-level docs should link only to [research/README.md](research/README.md), not to individual archival reports unless a specific historical reference is needed.
