# Manual Test Reports

This folder stores manual contract test runs.

## Layout

- One subfolder per run timestamp: `docs/manual_test/<YYYYMMDD_HHMMSS>/`
- Each run folder contains:
  - one subfolder per kwargs profile (`profile_a`, `profile_b`, ...)
  - each profile subfolder contains:
    - `contract_methods_manual_test_report.json`
    - `contract_methods_manual_test_report.html`
  - `summary.json`

## Run command

From repository root:

```bash
PYTHONPATH=src python3 scripts/manual_test_contracts.py --workers 8 --runs 2
```

The script creates a new timestamped run folder automatically.

Generated run folders are local artifacts and should not be committed.
Keep only this README and `kwargs_profiles.json` under version control.

Default run behavior:
- kwargs profiles are read from `docs/manual_test/kwargs_profiles.json`.
- current profile set contains `7` profiles (`profile_a` ... `profile_g`).
- attempts cycle through profiles in order (`attempt 1 -> profile_a`, `attempt 2 -> profile_b`, and so on).
- HTML report shows kwargs and output directly in table rows (without collapsing).

## Render HTML from existing JSON

```bash
PYTHONPATH=src python3 scripts/manual_test_contracts.py --from-json docs/manual_test/<RUN_ID>/<PROFILE>/contract_methods_manual_test_report.json
```
