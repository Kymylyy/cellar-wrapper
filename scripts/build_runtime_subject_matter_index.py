#!/usr/bin/env python3
"""Build packaged runtime subject-matter index from research snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path("docs/artifact/subject_matter_all.json")
DEFAULT_OUTPUT = Path("src/cellar_wrapper/data/subject_matter_index.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build runtime subject-matter index JSON for package data."
    )
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help=f"Input JSON (default: {DEFAULT_INPUT})")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help=f"Output JSON (default: {DEFAULT_OUTPUT})")
    return parser.parse_args()


def _load_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Input payload is not an object: {path}")
    results = payload.get("results")
    if not isinstance(results, dict):
        raise SystemExit(f"Input payload missing results object: {path}")
    bindings = results.get("bindings")
    if not isinstance(bindings, list):
        raise SystemExit(f"Input payload missing results.bindings list: {path}")
    return bindings


def _extract_runtime_rows(bindings: list[dict[str, Any]]) -> list[dict[str, str]]:
    seen_pairs: set[tuple[str, str]] = set()
    records: list[dict[str, str]] = []

    for row_index, row in enumerate(bindings):
        if not isinstance(row, dict):
            raise SystemExit(f"Row #{row_index} is not an object")

        concept_obj = row.get("sm")
        label_obj = row.get("label")
        concept_uri = concept_obj.get("value") if isinstance(concept_obj, dict) else None
        label = label_obj.get("value") if isinstance(label_obj, dict) else None

        if not isinstance(concept_uri, str) or not concept_uri.strip():
            raise SystemExit(f"Row #{row_index} missing concept URI")
        if not isinstance(label, str) or not label.strip():
            raise SystemExit(f"Row #{row_index} missing label")

        normalized_concept = concept_uri.strip()
        normalized_label = label.strip()
        pair = (normalized_concept, normalized_label)
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        records.append({"concept_uri": normalized_concept, "label": normalized_label})

    records.sort(key=lambda item: (item["label"], item["concept_uri"]))
    return records


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    bindings = _load_rows(input_path)
    records = _extract_runtime_rows(bindings)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(records, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Input rows: {len(bindings)}")
    print(f"Runtime rows: {len(records)}")
    print(f"Output: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
