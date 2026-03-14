# Documentation

If you just want to use the project, start here:

- [COMMAND_GUIDE.md](COMMAND_GUIDE.md): the quickest way to find the right CLI or MCP command.
- [CONTRACT_REFERENCE.md](CONTRACT_REFERENCE.md): exact input/output behavior, envelopes, caveats, and MCP notes.
- [CONTRACT_EXAMPLES.md](CONTRACT_EXAMPLES.md): readable examples of common or representative calls.

## How to read these docs

- The guide and examples are for humans.
- The reference is the maintained behavior document.
- The full command surface is covered by code-driven metadata and tests, not by the examples page.

That split matters:

- `docs/examples/contract-examples.json` is a curated set of examples worth showing to people.
- `docs/CONTRACT_EXAMPLES.md` is just the generated Markdown render of that curated set.
- `docs/artifact/command-manifest.json` is the machine-readable full command/contract coverage artifact.

So if a command exists but is not shown in the examples page, that is expected. Examples are curated; coverage lives elsewhere.

## Maintainer references

- [MAINTAINER_GUIDE.md](MAINTAINER_GUIDE.md): refresh workflow for examples, manifests, and live audits.
- [METHOD_MAPPING.md](METHOD_MAPPING.md): method-to-predicate mapping and SPARQL/CDM semantics.
- [DATA_ARTIFACTS.md](DATA_ARTIFACTS.md): policy for large non-runtime artifacts under `docs/artifact/`.
- [DATA_PROVENANCE.md](DATA_PROVENANCE.md): provenance and freshness policy for packaged runtime indexes.

## Archive

- [research/README.md](research/README.md): historical research and design notes.
- Files under `docs/research/` may differ from current runtime behavior.
- Files under `docs/artifact/` are support artifacts, not the public runtime contract by themselves.
