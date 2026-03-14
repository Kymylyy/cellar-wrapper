from __future__ import annotations

import json

from cellar_wrapper.contract_manifest import build_command_manifest, render_manifest_json


def test_build_command_manifest_includes_parameters_and_return_contract() -> None:
    manifest = build_command_manifest()
    resolve_celex = next(item for item in manifest if item["full_name"] == "lookup resolve-celex")

    assert resolve_celex["method"] == "resolve_celex"
    assert resolve_celex["parameters"] == [
        {
            "name": "celex",
            "kind": "celex",
            "cli_option": "--celex",
            "help_text": "CELEX identifier.",
            "required": True,
            "is_list": False,
        }
    ]
    assert resolve_celex["return_contract"] == {
        "return_type": "ActRef",
        "item_type": None,
        "query_name": None,
    }


def test_render_manifest_json_is_valid_json() -> None:
    payload = json.loads(render_manifest_json())

    assert isinstance(payload, list)
    assert payload
    assert all("full_name" in item for item in payload)
