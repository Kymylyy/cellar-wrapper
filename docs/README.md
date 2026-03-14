# Documentation

Use this page as the entry point for both active documentation and archival
material.

## Start here

- [COMMAND_GUIDE.md](COMMAND_GUIDE.md): plain-language guide for choosing and running CLI or MCP commands.
- [CONTRACT_REFERENCE.md](CONTRACT_REFERENCE.md): maintained reference for envelopes, inputs, return types, caveats, and MCP behavior.
- [CONTRACT_EXAMPLES.md](CONTRACT_EXAMPLES.md): generated examples based on accepted live payloads.

## Maintainer references

- [MAINTAINER_GUIDE.md](MAINTAINER_GUIDE.md): how to refresh contract examples, run live audits, and keep docs in sync after contract changes.
- [METHOD_MAPPING.md](METHOD_MAPPING.md): method-to-predicate mapping and SPARQL/CDM semantics.
- [DATA_ARTIFACTS.md](DATA_ARTIFACTS.md): inventory and maintenance policy for large non-runtime artifacts kept under `docs/artifact/`.
- [DATA_PROVENANCE.md](DATA_PROVENANCE.md): provenance, attribution, and freshness policy for packaged runtime indexes.

## Source-of-truth policy

- Command inventory, argument/default behavior, and return-model mapping come from code, chiefly `cli_specs.py`, `cli_policy.py`, and `contract_specs.py`.
- Accepted example payloads come from `docs/examples/contract-examples.json`; the Markdown examples page is a generated render of that file.
- Narrative docs explain and contextualize maintained behavior; they should not invent a second source of truth.

## Archive

- [research/README.md](research/README.md): archival research and historical design notes.
- Files under `docs/research/` were part of the initial discovery/design process and may differ from current runtime behavior or accepted examples.
- Files under `docs/artifact/` are support material, not runtime contract.
