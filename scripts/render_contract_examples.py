from __future__ import annotations

import importlib.util
import json
import shlex
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"


def _load_cli_specs_module() -> Any:
    module_path = SRC / "cellar_wrapper" / "cli_specs.py"
    spec = importlib.util.spec_from_file_location("temp_cli_specs", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load cli_specs module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_CLI_SPECS = _load_cli_specs_module()
COMMANDS = _CLI_SPECS.COMMANDS

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
    command_specs: Sequence[Any] = COMMANDS,
) -> None:
    known_commands = {f"{spec.group} {spec.command}" for spec in command_specs}
    example_commands = [str(example.get("command", "")) for example in examples]

    unknown_commands = sorted({command for command in example_commands if command not in known_commands})
    if unknown_commands:
        raise ValueError(f"Unknown commands in contract examples: {', '.join(unknown_commands)}")

    missing_commands = sorted(known_commands.difference(example_commands))
    if missing_commands:
        raise ValueError(f"Missing contract examples for commands: {', '.join(missing_commands)}")

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
    command_specs: Sequence[Any] = COMMANDS,
) -> str:
    validate_examples(examples, command_specs=command_specs)

    grouped_examples: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for example in examples:
        grouped_examples[str(example["command"])].append(example)

    lines = [
        "# Contract Examples",
        "",
        "Generated from `docs/examples/contract-examples.json`.",
        "Source of truth remains the JSON file; this Markdown is a readable render.",
        "",
    ]

    seen_groups: set[str] = set()
    for spec in command_specs:
        group_name = spec.group
        command_name = f"{spec.group} {spec.command}"
        if group_name not in seen_groups:
            seen_groups.add(group_name)
            lines.extend([f"## {GROUP_TITLES.get(group_name, group_name.upper())}", ""])

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


def main() -> int:
    try:
        examples = load_contract_examples(DEFAULT_INPUT_PATH)
        markdown = render_markdown(examples)
        DEFAULT_OUTPUT_PATH.write_text(markdown, encoding="utf-8")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {DEFAULT_OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
