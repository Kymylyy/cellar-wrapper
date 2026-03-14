from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cellar_wrapper.contract_manifest import DEFAULT_OUTPUT_PATH, render_manifest_json  # noqa: E402


def main() -> int:
    try:
        DEFAULT_OUTPUT_PATH.write_text(render_manifest_json(), encoding="utf-8")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {DEFAULT_OUTPUT_PATH.relative_to(DEFAULT_OUTPUT_PATH.parents[2])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
