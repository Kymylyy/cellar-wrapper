from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import cellar_wrapper.contract_examples as contract_examples  # noqa: E402

normalize_payload = contract_examples.normalize_payload


def main() -> int:
    examples = contract_examples.load_contract_examples(contract_examples.DEFAULT_INPUT_PATH)
    failures = contract_examples.audit_examples_live(examples)

    if failures:
        print("Contract examples live audit failed.\n", file=sys.stderr)
        print("\n\n".join(failures), file=sys.stderr)
        return 1

    print(f"Live audit matched {len(examples)} curated contract examples.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
