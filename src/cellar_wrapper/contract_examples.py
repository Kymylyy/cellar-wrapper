"""Helpers for curated contract examples and their Markdown render."""

from __future__ import annotations

import difflib
import json
import os
import shlex
import subprocess
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from typing import Any

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


def audit_examples_live(examples: Sequence[Mapping[str, Any]]) -> list[str]:
    validate_examples(examples)
    env = build_cli_env()
    failures: list[str] = []

    for example in examples:
        completed = subprocess.run(
            build_cli_argv(example),
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        command_label = f"{example['command']} [{example['label']}]"
        if completed.returncode != 0:
            failures.append(
                "\n".join(
                    [
                        f"## {command_label}",
                        f"CLI exited with {completed.returncode}",
                        completed.stderr.strip() or completed.stdout.strip() or "<no output>",
                    ]
                )
            )
            continue

        try:
            actual_payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(
                "\n".join(
                    [
                        f"## {command_label}",
                        f"Failed to decode CLI JSON output: {exc}",
                        completed.stdout.strip() or "<empty stdout>",
                    ]
                )
            )
            continue

        expected_payload = normalize_payload(example["output"])
        actual_normalized = normalize_payload(actual_payload)
        if actual_normalized != expected_payload:
            failures.append(
                "\n".join(
                    [
                        f"## {command_label}",
                        diff_payloads(expected_payload, actual_normalized),
                    ]
                )
            )

    return failures


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
