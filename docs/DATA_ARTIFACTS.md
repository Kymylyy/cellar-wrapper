# Data Artifacts

This document explains large non-code files stored in `docs/`.

## Purpose

These files are research/support artifacts for exploration and analysis. They are
not consumed by the runtime package (`src/cellar_wrapper`) and should not be
treated as API contract.

## Inventory

| File | Role |
| --- | --- |
| `eurovoc_all.json` | Snapshot of EuroVoc concept data used during taxonomy analysis. |
| `eurovoc_with_groups.json` | Enriched EuroVoc snapshot with group/microthesaurus metadata. |
| `eurovoc_microthesauri.json` | Compact mapping of EuroVoc microthesauri. |
| `eurovoc_concepts.csv` | Tabular export of EuroVoc concepts. |
| `subject_matter_all.json` | Snapshot of subject-matter authority data. |
| `subject_matter_counts.json` | Aggregate counts for subject-matter exploration. |
| `subject_matter.csv` | Tabular export of subject-matter terms. |
| `eurovoc_explorer.html` | Local static explorer UI for EuroVoc dataset inspection. |
| `taxonomy_explorer.html` | Local static explorer UI for taxonomy/subject-matter inspection. |

## Maintenance policy

- Keep artifacts only when they support active docs/research workflows.
- If an artifact is superseded, replace it in-place or remove it in the same
  commit as related doc updates.
- Any behavioral/API changes must be documented in `API_CONTRACT.md`, not here.
