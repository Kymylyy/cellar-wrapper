from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import cellar_wrapper.contract_examples as contract_examples  # noqa: E402

normalize_payload = contract_examples.normalize_payload


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"expected integer, got {value!r}") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be >= 1")
    return parsed


def _positive_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"expected number, got {value!r}") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be > 0")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="audit_contract_examples_live.py")
    parser.add_argument("--mode", choices=("full", "smoke"), default="full")
    parser.add_argument(
        "--command",
        action="append",
        default=[],
        help='Repeatable exact full command name, for example "lookup get-act".',
    )
    parser.add_argument(
        "--group",
        action="append",
        default=[],
        help='Repeatable exact command group, for example "lookup".',
    )
    parser.add_argument(
        "--label",
        action="append",
        default=[],
        help='Repeatable exact curated example label, for example "MiCA".',
    )
    parser.add_argument("--limit", type=_positive_int, default=None, help="Maximum examples to run.")
    parser.add_argument("--fail-fast", action="store_true", help="Stop after the first failure.")
    parser.add_argument(
        "--timeout-seconds",
        type=_positive_float,
        default=30.0,
        help="Per-example subprocess timeout in seconds.",
    )
    parser.add_argument(
        "--slow-threshold-seconds",
        type=_positive_float,
        default=10.0,
        help="Mark examples slower than this threshold in progress output.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    examples = contract_examples.load_contract_examples(contract_examples.DEFAULT_INPUT_PATH)
    options = contract_examples.ContractExamplesAuditOptions(
        smoke=args.mode == "smoke",
        command_filter=frozenset(args.command),
        group_filter=frozenset(args.group),
        label_filter=frozenset(args.label),
        limit=args.limit,
        timeout_seconds=args.timeout_seconds,
        slow_threshold_seconds=args.slow_threshold_seconds,
        fail_fast=args.fail_fast,
    )

    run = contract_examples.audit_examples_live_detailed(
        examples,
        options=options,
        progress_handler=lambda line: print(line, file=sys.stderr),
        result_handler=lambda line: print(line, file=sys.stderr),
    )

    if not run.selected_examples:
        print("No curated contract examples matched the selected filters.", file=sys.stderr)
        return 0

    if run.failure_records:
        failure_blocks = contract_examples.render_audit_failures(run)
        print("Contract examples live audit failed.\n", file=sys.stderr)
        print("\n".join(contract_examples.render_audit_summary(run)), file=sys.stderr)
        print("", file=sys.stderr)
        print("\n\n".join(failure_blocks[1:]), file=sys.stderr)
        return 1

    print("\n".join(contract_examples.render_audit_summary(run)), file=sys.stderr)
    print(
        f"Live audit matched {len(run.selected_examples)} curated contract examples "
        f"(mode={args.mode})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
