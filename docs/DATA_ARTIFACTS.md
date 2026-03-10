# Data Artifacts

This document explains large non-code files stored in `docs/artifact/`.

## Purpose

These files are research/support artifacts for exploration and analysis.
They are not consumed directly by runtime code.
Runtime resolve uses packaged data files:
`src/cellar_wrapper/data/eurovoc_index.json` and
`src/cellar_wrapper/data/subject_matter_index.json`.
Source attribution and reuse notes are documented in `DATA_PROVENANCE.md`.

## Inventory

| File | Role |
| --- | --- |
| `artifact/eurovoc_all.json` | Snapshot of EuroVoc concept data used during taxonomy analysis. |
| `artifact/eurovoc_with_groups.json` | Enriched EuroVoc snapshot with group/microthesaurus metadata. |
| `artifact/eurovoc_microthesauri.json` | Compact mapping of EuroVoc microthesauri. |
| `artifact/eurovoc_concepts.csv` | Tabular export of EuroVoc concepts. |
| `artifact/subject_matter_all.json` | Snapshot of subject-matter authority data. |
| `artifact/subject_matter_counts.json` | Aggregate counts for subject-matter exploration. |
| `artifact/subject_matter.csv` | Tabular export of subject-matter terms. |
| `artifact/eurovoc_explorer.html` | Local static explorer UI for EuroVoc dataset inspection. |
| `artifact/taxonomy_explorer.html` | Local static explorer UI for taxonomy/subject-matter inspection. |

## Maintenance policy

- Keep artifacts only when they support active docs/research workflows.
- If an artifact is superseded, replace it in-place or remove it in the same
  commit as related doc updates.
- Any behavioral/API changes must be documented in `API_CONTRACT.md`, not here.
- Refresh packaged runtime EuroVoc index with:
  `python3 scripts/build_runtime_eurovoc_index.py`
- Refresh packaged runtime subject-matter index with:
  `python3 scripts/build_runtime_subject_matter_index.py`
