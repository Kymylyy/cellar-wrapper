from __future__ import annotations

import difflib
import importlib.util
import json
import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
RENDER_SCRIPT = ROOT / "scripts" / "render_contract_examples.py"
VOLATILE_PATHS: tuple[tuple[str, ...], ...] = (("data", "meta", "executed_at"),)
ORDER_INSENSITIVE_PATHS: tuple[tuple[str, ...], ...] = (("data", "items"),)
COMMAND_TIMEOUT_SECONDS = 120


def _load_render_module() -> Any:
    spec = importlib.util.spec_from_file_location("render_contract_examples", RENDER_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load render module from {RENDER_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _remove_path(payload: Any, path: tuple[str, ...]) -> None:
    cursor = payload
    for key in path[:-1]:
        if not isinstance(cursor, dict) or key not in cursor:
            return
        cursor = cursor[key]

    if isinstance(cursor, dict):
        cursor.pop(path[-1], None)


def _sort_for_compare(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _sort_for_compare(item) for key, item in value.items()}
    if isinstance(value, list):
        normalized = [_sort_for_compare(item) for item in value]
        return sorted(
            normalized,
            key=lambda item: json.dumps(item, ensure_ascii=False, sort_keys=True),
        )
    return value


def _sort_path(payload: Any, path: tuple[str, ...]) -> None:
    cursor = payload
    for key in path[:-1]:
        if not isinstance(cursor, dict) or key not in cursor:
            return
        cursor = cursor[key]

    if isinstance(cursor, dict) and path[-1] in cursor:
        cursor[path[-1]] = _sort_for_compare(cursor[path[-1]])


def normalize_payload(payload: Any) -> Any:
    normalized = deepcopy(payload)
    for path in VOLATILE_PATHS:
        _remove_path(normalized, path)
    for path in ORDER_INSENSITIVE_PATHS:
        _sort_path(normalized, path)
    return normalized


def _cli_argv(render_module: Any, example: dict[str, Any]) -> list[str]:
    cli_parts = render_module.build_cli_parts(example["command"], example["args"])
    return [sys.executable, "-m", "cellar_wrapper.cli", *cli_parts[1:]]


def _cli_env() -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(SRC) if not existing else f"{SRC}{os.pathsep}{existing}"
    return env


def _diff(expected: Any, actual: Any) -> str:
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


def main() -> int:
    render_module = _load_render_module()
    examples = render_module.load_contract_examples(render_module.DEFAULT_INPUT_PATH)
    render_module.validate_examples(examples)
    env = _cli_env()

    failures: list[str] = []
    for example in examples:
        argv = _cli_argv(render_module, example)
        command_label = f"{example['command']} [{example['label']}]"
        print(f"Auditing {command_label}", file=sys.stderr, flush=True)
        try:
            completed = subprocess.run(
                argv,
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
                timeout=COMMAND_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            failures.append(
                "\n".join(
                    [
                        f"## {command_label}",
                        f"CLI timed out after {COMMAND_TIMEOUT_SECONDS}s",
                    ]
                )
            )
            continue

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
                        _diff(expected_payload, actual_normalized),
                    ]
                )
            )

    if failures:
        print("Contract examples live audit failed.\n", file=sys.stderr)
        print("\n\n".join(failures), file=sys.stderr)
        return 1

    print(f"Live audit matched {len(examples)} contract examples.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
