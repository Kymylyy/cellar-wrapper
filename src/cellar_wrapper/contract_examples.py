"""Helpers for curated contract examples and their Markdown render."""

from __future__ import annotations

import difflib
import json
import os
import shlex
import subprocess
import sys
from collections import defaultdict
from collections.abc import Callable, Collection, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Any, Literal

from cellar_wrapper.cli_specs import COMMANDS, CommandSpec

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_PATH = ROOT / "docs" / "examples" / "contract-examples.json"
DEFAULT_OUTPUT_PATH = ROOT / "docs" / "CONTRACT_EXAMPLES.md"

GROUP_TITLES = {
    "lookup": "LOOKUP",
    "relations": "RELATIONS",
    "lifecycle": "LIFECYCLE",
    "case-law": "CASE LAW",
    "search": "SEARCH",
    "monitoring": "MONITORING",
    "download": "DOWNLOAD",
}
CONTENT_BASE64_PREVIEW_CHARS = 120
VOLATILE_PATHS: tuple[tuple[str, ...], ...] = (("data", "meta", "executed_at"),)
SMOKE_EXAMPLE_KEYS: tuple[tuple[str, str], ...] = (
    ("lookup resolve-celex", "DORA"),
    ("lookup get-act", "MiCA"),
    ("relations get-amendments", "PSR"),
    ("lifecycle get-consolidated-versions", "PSD2"),
    ("case-law get-cjeu-judgments", "PSD2"),
    ("search search-by-title", "Crypto-assets"),
    ("monitoring new-citations", "MiCA"),
    ("download get-summary", "DORA"),
)
STDIO_EXCERPT_CHARS = 800
SLOW_SUMMARY_LIMIT = 5
AuditStatus = Literal["passed", "cli_error", "decode_error", "mismatch", "timeout"]


@dataclass(frozen=True)
class AuditExampleRef:
    index: int
    command: str
    group: str
    label: str
    cli: str
    example: Mapping[str, Any]


@dataclass(frozen=True)
class ContractExamplesAuditOptions:
    smoke: bool = False
    command_filter: frozenset[str] = frozenset()
    group_filter: frozenset[str] = frozenset()
    label_filter: frozenset[str] = frozenset()
    limit: int | None = None
    timeout_seconds: float | None = None
    slow_threshold_seconds: float | None = None
    fail_fast: bool = False


@dataclass(frozen=True)
class ContractExampleAuditRecord:
    example: AuditExampleRef
    position: int
    total: int
    status: AuditStatus
    elapsed_seconds: float
    is_slow: bool
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    summary: str = ""
    details: str = ""

    @property
    def failed(self) -> bool:
        return self.status != "passed"


@dataclass(frozen=True)
class ContractExamplesAuditRun:
    options: ContractExamplesAuditOptions
    total_examples: int
    selected_examples: list[AuditExampleRef] = field(default_factory=list)
    records: list[ContractExampleAuditRecord] = field(default_factory=list)

    @property
    def failure_records(self) -> list[ContractExampleAuditRecord]:
        return [record for record in self.records if record.failed]

    @property
    def passed_records(self) -> list[ContractExampleAuditRecord]:
        return [record for record in self.records if not record.failed]

    @property
    def timed_out_records(self) -> list[ContractExampleAuditRecord]:
        return [record for record in self.records if record.status == "timeout"]

    @property
    def total_elapsed_seconds(self) -> float:
        return sum(record.elapsed_seconds for record in self.records)


def load_contract_examples(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Contract examples payload must be a list: {path}")
    examples: list[dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"Contract example #{index + 1} must be an object")
        examples.append(item)
    return examples


def validate_examples(
    examples: Sequence[Mapping[str, Any]],
    command_specs: Sequence[CommandSpec] = COMMANDS,
) -> None:
    known_commands = {spec.full_name for spec in command_specs}
    example_commands = [str(example.get("command", "")) for example in examples]

    unknown_commands = sorted({command for command in example_commands if command not in known_commands})
    if unknown_commands:
        raise ValueError(f"Unknown commands in contract examples: {', '.join(unknown_commands)}")

    for index, example in enumerate(examples):
        for field_name in ("label", "purpose"):
            value = example.get(field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Contract example #{index + 1} must contain non-empty string `{field_name}`"
                )
        celex_value = example.get("celex")
        if celex_value is not None and (not isinstance(celex_value, str) or not celex_value.strip()):
            raise ValueError(
                f"Contract example #{index + 1} must contain string `celex` or null"
            )
        if "args" not in example or not isinstance(example["args"], dict):
            raise ValueError(f"Contract example #{index + 1} must contain an object `args`")
        if "output" not in example:
            raise ValueError(f"Contract example #{index + 1} must contain `output`")


def build_cli_parts(command: str, args: Mapping[str, Any]) -> list[str]:
    parts = ["cellar", *command.split()]
    for key, value in args.items():
        option_name = f"--{key.replace('_', '-')}"
        parts.append(option_name)

        if isinstance(value, list):
            if not value:
                raise ValueError(f"Argument `{key}` must not be an empty list")
            for item in value:
                if isinstance(item, bool) or item is None:
                    raise ValueError(f"Unsupported value for list argument `{key}`: {item!r}")
                parts.append(str(item))
            continue

        if isinstance(value, bool) or value is None:
            raise ValueError(f"Unsupported value for argument `{key}`: {value!r}")
        parts.append(str(value))

    return parts


def render_cli(command: str, args: Mapping[str, Any]) -> str:
    return shlex.join(build_cli_parts(command, args))


def _remove_path(payload: Any, path: tuple[str, ...]) -> None:
    cursor = payload
    for key in path[:-1]:
        if not isinstance(cursor, dict) or key not in cursor:
            return
        cursor = cursor[key]

    if isinstance(cursor, dict):
        cursor.pop(path[-1], None)


def _sort_key(value: Any) -> str:
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return repr(value)


def _normalize_collection(value: list[Any]) -> list[Any]:
    normalized_items = [_normalize_value(item) for item in value]
    if not normalized_items:
        return normalized_items
    if all(not isinstance(item, (dict, list)) for item in normalized_items):
        return sorted(normalized_items, key=_sort_key)
    if all(isinstance(item, dict) for item in normalized_items):
        return sorted(normalized_items, key=_sort_key)
    return normalized_items


def _normalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _normalize_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return _normalize_collection(value)
    return value


def normalize_payload(payload: Any) -> Any:
    normalized = deepcopy(payload)
    for path in VOLATILE_PATHS:
        _remove_path(normalized, path)
    return _normalize_value(normalized)


def build_cli_argv(example: Mapping[str, Any]) -> list[str]:
    cli_parts = build_cli_parts(str(example["command"]), example["args"])
    return [sys.executable, "-m", "cellar_wrapper.cli", *cli_parts[1:]]


def build_cli_env() -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    src = ROOT / "src"
    env["PYTHONPATH"] = str(src) if not existing else f"{src}{os.pathsep}{existing}"
    return env


def diff_payloads(expected: Any, actual: Any) -> str:
    expected_text = json.dumps(expected, ensure_ascii=False, indent=2, sort_keys=True)
    actual_text = json.dumps(actual, ensure_ascii=False, indent=2, sort_keys=True)
    return "\n".join(
        difflib.unified_diff(
            expected_text.splitlines(),
            actual_text.splitlines(),
            fromfile="expected",
            tofile="actual",
            lineterm="",
        )
    )


def _coerce_exact_filter(values: str | Collection[str] | None) -> frozenset[str]:
    if values is None:
        return frozenset()
    if isinstance(values, str):
        normalized = values.strip()
        return frozenset({normalized}) if normalized else frozenset()

    normalized_values: list[str] = []
    for value in values:
        normalized = str(value).strip()
        if normalized:
            normalized_values.append(normalized)
    return frozenset(normalized_values)


def group_from_command(command: str) -> str:
    return command.split(maxsplit=1)[0] if command else ""


def _build_audit_example_refs(examples: Sequence[Mapping[str, Any]]) -> list[AuditExampleRef]:
    refs: list[AuditExampleRef] = []
    for index, example in enumerate(examples, start=1):
        command = str(example["command"])
        refs.append(
            AuditExampleRef(
                index=index,
                command=command,
                group=group_from_command(command),
                label=str(example["label"]),
                cli=render_cli(command, example["args"]),
                example=example,
            )
        )
    return refs


def _select_smoke_examples(selected: Sequence[AuditExampleRef]) -> list[AuditExampleRef]:
    first_match_by_key: dict[tuple[str, str], AuditExampleRef] = {}
    smoke_keys = set(SMOKE_EXAMPLE_KEYS)
    for ref in selected:
        key = (ref.command, ref.label)
        if key in smoke_keys and key not in first_match_by_key:
            first_match_by_key[key] = ref
    return [first_match_by_key[key] for key in SMOKE_EXAMPLE_KEYS if key in first_match_by_key]


def select_audit_examples(
    examples: Sequence[Mapping[str, Any]],
    *,
    smoke: bool = False,
    command_filter: str | Collection[str] | None = None,
    group_filter: str | Collection[str] | None = None,
    label_filter: str | Collection[str] | None = None,
    limit: int | None = None,
) -> list[AuditExampleRef]:
    validate_examples(examples)
    selected = _build_audit_example_refs(examples)

    exact_commands = _coerce_exact_filter(command_filter)
    exact_groups = _coerce_exact_filter(group_filter)
    exact_labels = _coerce_exact_filter(label_filter)

    if exact_commands:
        selected = [ref for ref in selected if ref.command in exact_commands]
    if exact_groups:
        selected = [ref for ref in selected if ref.group in exact_groups]
    if exact_labels:
        selected = [ref for ref in selected if ref.label in exact_labels]

    if smoke:
        selected = _select_smoke_examples(selected)

    if limit is not None:
        if limit < 0:
            raise ValueError("limit must be >= 0")
        selected = selected[:limit]

    return selected


def format_audit_progress_line(example: AuditExampleRef, *, position: int, total: int) -> str:
    return f"[{position}/{total}] RUN {example.command} [{example.label}]"


def format_audit_result_line(record: ContractExampleAuditRecord) -> str:
    status = "PASS" if record.status == "passed" else record.status.upper()
    slow_suffix = " SLOW" if record.is_slow else ""
    return (
        f"[{record.position}/{record.total}] {status}{slow_suffix} {record.elapsed_seconds:.2f}s "
        f"{record.example.command} [{record.example.label}]"
    )


def _timeout_details(exc: subprocess.TimeoutExpired) -> str:
    stdout = exc.stdout.strip() if isinstance(exc.stdout, str) else ""
    stderr = exc.stderr.strip() if isinstance(exc.stderr, str) else ""
    tail = stderr or stdout or "<no output>"
    return "\n".join([f"Timed out after {exc.timeout:.2f}s", _bounded_excerpt(tail)])


def _bounded_excerpt(text: str, *, limit: int = STDIO_EXCERPT_CHARS) -> str:
    normalized = text.strip()
    if not normalized:
        return "<no output>"
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[:limit]}... [truncated, total length {len(normalized)}]"


def audit_examples_live_detailed(
    examples: Sequence[Mapping[str, Any]],
    *,
    options: ContractExamplesAuditOptions | None = None,
    env: Mapping[str, str] | None = None,
    progress_handler: Callable[[str], None] | None = None,
    result_handler: Callable[[str], None] | None = None,
) -> ContractExamplesAuditRun:
    validate_examples(examples)
    resolved_options = options or ContractExamplesAuditOptions()
    resolved_env = dict(build_cli_env() if env is None else env)
    selected_examples = select_audit_examples(
        examples,
        smoke=resolved_options.smoke,
        command_filter=resolved_options.command_filter,
        group_filter=resolved_options.group_filter,
        label_filter=resolved_options.label_filter,
        limit=resolved_options.limit,
    )
    records: list[ContractExampleAuditRecord] = []
    total = len(selected_examples)

    for position, selected in enumerate(selected_examples, start=1):
        if progress_handler is not None:
            progress_handler(format_audit_progress_line(selected, position=position, total=total))

        start = perf_counter()
        try:
            completed = subprocess.run(
                build_cli_argv(selected.example),
                cwd=ROOT,
                env=resolved_env,
                capture_output=True,
                text=True,
                check=False,
                timeout=resolved_options.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            elapsed_seconds = perf_counter() - start
            record = ContractExampleAuditRecord(
                example=selected,
                position=position,
                total=total,
                status="timeout",
                elapsed_seconds=elapsed_seconds,
                is_slow=(
                    resolved_options.slow_threshold_seconds is not None
                    and elapsed_seconds >= resolved_options.slow_threshold_seconds
                ),
                summary=f"Timed out after {exc.timeout:.2f}s",
                details=_timeout_details(exc),
            )
            records.append(record)
            if result_handler is not None:
                result_handler(format_audit_result_line(record))
            if resolved_options.fail_fast:
                break
            continue

        elapsed_seconds = perf_counter() - start
        is_slow = (
            resolved_options.slow_threshold_seconds is not None
            and elapsed_seconds >= resolved_options.slow_threshold_seconds
        )

        if completed.returncode != 0:
            record = ContractExampleAuditRecord(
                example=selected,
                position=position,
                total=total,
                status="cli_error",
                elapsed_seconds=elapsed_seconds,
                is_slow=is_slow,
                returncode=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                summary=f"CLI exited with {completed.returncode}",
                details=_bounded_excerpt(completed.stderr or completed.stdout),
            )
            records.append(record)
            if result_handler is not None:
                result_handler(format_audit_result_line(record))
            if resolved_options.fail_fast:
                break
            continue

        try:
            actual_payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            record = ContractExampleAuditRecord(
                example=selected,
                position=position,
                total=total,
                status="decode_error",
                elapsed_seconds=elapsed_seconds,
                is_slow=is_slow,
                returncode=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                summary=f"Failed to decode CLI JSON output: {exc}",
                details=_bounded_excerpt(completed.stdout),
            )
            records.append(record)
            if result_handler is not None:
                result_handler(format_audit_result_line(record))
            if resolved_options.fail_fast:
                break
            continue

        expected_payload = normalize_payload(selected.example["output"])
        actual_normalized = normalize_payload(actual_payload)
        if actual_normalized != expected_payload:
            record = ContractExampleAuditRecord(
                example=selected,
                position=position,
                total=total,
                status="mismatch",
                elapsed_seconds=elapsed_seconds,
                is_slow=is_slow,
                returncode=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                summary="Live output did not match curated example",
                details=diff_payloads(expected_payload, actual_normalized),
            )
            records.append(record)
            if result_handler is not None:
                result_handler(format_audit_result_line(record))
            if resolved_options.fail_fast:
                break
            continue

        record = ContractExampleAuditRecord(
            example=selected,
            position=position,
            total=total,
            status="passed",
            elapsed_seconds=elapsed_seconds,
            is_slow=is_slow,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            summary="Matched curated example",
        )
        records.append(record)
        if result_handler is not None:
            result_handler(format_audit_result_line(record))

    return ContractExamplesAuditRun(
        options=resolved_options,
        total_examples=len(examples),
        selected_examples=selected_examples,
        records=records,
    )


def render_audit_failures(run: ContractExamplesAuditRun) -> list[str]:
    failure_records = run.failure_records
    if not failure_records:
        return []

    summary = (
        "Audit failures: "
        f"{len(failure_records)} of {len(run.records)} executed "
        f"({len(run.selected_examples)} selected from {run.total_examples} total examples)."
    )
    rendered = [summary]
    for record in failure_records:
        rendered.append(
            "\n".join(
                [
                    f"## {record.example.command} [{record.example.label}]",
                    f"CLI: {record.example.cli}",
                    f"Status: {record.status}",
                    f"Elapsed: {record.elapsed_seconds:.2f}s",
                    record.summary,
                    record.details or "<no details>",
                ]
            )
        )
    return rendered


def render_audit_summary(run: ContractExamplesAuditRun) -> list[str]:
    lines = [
        "Audit summary:",
        f"- selected: {len(run.selected_examples)} of {run.total_examples}",
        f"- executed: {len(run.records)}",
        f"- passed: {len(run.passed_records)}",
        f"- failed: {len(run.failure_records)}",
        f"- timed_out: {len(run.timed_out_records)}",
        f"- total_runtime_s: {run.total_elapsed_seconds:.2f}",
    ]
    slowest_records = sorted(
        run.records,
        key=lambda record: record.elapsed_seconds,
        reverse=True,
    )[:SLOW_SUMMARY_LIMIT]
    if slowest_records:
        lines.append("- slowest:")
        for record in slowest_records:
            lines.append(
                f"  - {record.elapsed_seconds:.2f}s {record.example.command} [{record.example.label}]"
            )
    return lines


def audit_examples_live(
    examples: Sequence[Mapping[str, Any]],
    *,
    smoke: bool = False,
    command_filter: str | Collection[str] | None = None,
    group_filter: str | Collection[str] | None = None,
    label_filter: str | Collection[str] | None = None,
    limit: int | None = None,
    timeout_seconds: float | None = None,
    slow_threshold_seconds: float | None = None,
    fail_fast: bool = False,
) -> list[str]:
    run = audit_examples_live_detailed(
        examples,
        options=ContractExamplesAuditOptions(
            smoke=smoke,
            command_filter=_coerce_exact_filter(command_filter),
            group_filter=_coerce_exact_filter(group_filter),
            label_filter=_coerce_exact_filter(label_filter),
            limit=limit,
            timeout_seconds=timeout_seconds,
            slow_threshold_seconds=slow_threshold_seconds,
            fail_fast=fail_fast,
        ),
    )
    return render_audit_failures(run)


def _markdown_friendly_value(value: Any) -> Any:
    if isinstance(value, dict):
        friendly: dict[str, Any] = {}
        for key, item in value.items():
            if key == "content_base64" and isinstance(item, str) and len(item) > CONTENT_BASE64_PREVIEW_CHARS:
                friendly[key] = (
                    f"{item[:CONTENT_BASE64_PREVIEW_CHARS]}..."
                    f" [truncated in docs, total length {len(item)}]"
                )
                continue
            friendly[key] = _markdown_friendly_value(item)
        return friendly
    if isinstance(value, list):
        return [_markdown_friendly_value(item) for item in value]
    return value


def render_markdown(
    examples: Sequence[Mapping[str, Any]],
    command_specs: Sequence[CommandSpec] = COMMANDS,
) -> str:
    validate_examples(examples, command_specs=command_specs)

    grouped_examples: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for example in examples:
        grouped_examples[str(example["command"])].append(example)

    lines = [
        "# Contract Examples",
        "",
        "Generated from `docs/examples/contract-examples.json`.",
        "Source of truth remains the JSON file; this Markdown is a readable render of curated examples.",
        "",
    ]

    seen_groups: set[str] = set()
    for spec in command_specs:
        command_name = spec.full_name
        if command_name not in grouped_examples:
            continue

        if spec.group not in seen_groups:
            seen_groups.add(spec.group)
            lines.extend([f"## {GROUP_TITLES.get(spec.group, spec.group.upper())}", ""])

        lines.extend([f"### `{command_name}`", ""])
        for index, example in enumerate(grouped_examples[command_name], start=1):
            label = str(example.get("label") or f"Example {index}")
            purpose = str(example.get("purpose") or "")
            cli = render_cli(command_name, example["args"])
            output_json = json.dumps(
                _markdown_friendly_value(example["output"]),
                ensure_ascii=False,
                indent=2,
            )

            lines.extend([f"#### {label}", ""])
            if purpose:
                lines.extend([f"Purpose: {purpose}", ""])
            lines.extend(
                [
                    "CLI:",
                    "```bash",
                    cli,
                    "```",
                    "",
                    "Output:",
                    "```json",
                    output_json,
                    "```",
                    "",
                ]
            )

    return "\n".join(lines).rstrip() + "\n"
