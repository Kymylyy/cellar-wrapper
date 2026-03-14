# Data Provenance

For the artifact inventory, see [DATA_ARTIFACTS.md](DATA_ARTIFACTS.md). For
the broader docs/update workflow, see [MAINTAINER_GUIDE.md](MAINTAINER_GUIDE.md).

This project ships runtime taxonomy indexes as package data:

- `src/cellar_wrapper/data/eurovoc_index.json`
- `src/cellar_wrapper/data/subject_matter_index.json`

## Upstream Sources

- EuroVoc concepts: `http://eurovoc.europa.eu`
- Publications Office authority resources (including subject-matter authority terms): `http://publications.europa.eu/resource/authority/`

## Generation Flow

1. Research snapshots are stored under `docs/` as documented in `DATA_ARTIFACTS.md`.
2. Runtime indexes are generated from those snapshots by:
   - `scripts/build_runtime_eurovoc_index.py`
   - `scripts/build_runtime_subject_matter_index.py`
3. Generated runtime files are committed under `src/cellar_wrapper/data/`.

## Attribution and Reuse

- Source vocabularies and authority data are owned by their respective publishers.
- This repository redistributes derived index artifacts to support local runtime resolution.
- Downstream users are responsible for validating legal reuse requirements for their distribution context.

## Freshness

- Snapshot freshness is tied to repository history.
- When taxonomy behavior changes, refresh snapshots and runtime indexes in the same pull request.
