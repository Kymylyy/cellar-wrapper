"""Helpers for generating a machine-readable command/contract manifest."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from cellar_wrapper.cli_specs import COMMANDS, CommandParameterSpec, CommandSpec, ReturnContract

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_PATH = ROOT / "docs" / "artifact" / "command-manifest.json"


def _serialize_parameter(param: CommandParameterSpec) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": param.name,
        "kind": param.kind,
        "cli_option": param.cli_option,
        "help_text": param.help_text,
        "required": param.required,
        "is_list": param.is_list,
    }
    if param.has_default:
        payload["default"] = param.default
    if param.choices is not None:
        payload["choices"] = list(param.choices)
    return payload


def _serialize_return_contract(contract: ReturnContract) -> dict[str, Any]:
    return {
        "return_type": contract.return_type.__name__,
        "item_type": contract.item_type.__name__ if contract.item_type is not None else None,
        "query_name": contract.query_name,
    }


def build_command_manifest(command_specs: Sequence[CommandSpec] = COMMANDS) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for spec in command_specs:
        manifest.append(
            {
                "group": spec.group,
                "command": spec.command,
                "full_name": spec.full_name,
                "method": spec.method,
                "description": spec.description,
                "parameters": [_serialize_parameter(param) for param in spec.parameters],
                "return_contract": _serialize_return_contract(spec.return_contract),
            }
        )
    return manifest


def render_manifest_json(command_specs: Sequence[CommandSpec] = COMMANDS) -> str:
    return json.dumps(build_command_manifest(command_specs), ensure_ascii=False, indent=2) + "\n"

