from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "audit_contract_examples_live.py"


def _load_audit_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("audit_contract_examples_live", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_normalize_payload_removes_volatile_timestamps() -> None:
    module = _load_audit_module()

    payload = {
        "ok": True,
        "data": {
            "items": [],
            "meta": {
                "executed_at": "2026-03-14T12:20:02.104208Z",
                "limit": 5,
            },
        },
    }

    normalized = module.normalize_payload(payload)

    assert "executed_at" not in normalized["data"]["meta"]
    assert normalized["data"]["meta"]["limit"] == 5


def test_normalize_payload_sorts_data_items_for_order_insensitive_audit() -> None:
    module = _load_audit_module()

    payload = {
        "ok": True,
        "data": {
            "items": [
                {
                    "uri": "http://example.test/b",
                    "celex": None,
                    "aliases": ["zeta", "alpha"],
                },
                {
                    "uri": "http://example.test/a",
                    "celex": "32022R2554",
                    "aliases": ["beta", "alpha"],
                },
            ]
        },
    }

    normalized = module.normalize_payload(payload)

    assert [item["uri"] for item in normalized["data"]["items"]] == [
        "http://example.test/a",
        "http://example.test/b",
    ]
    assert normalized["data"]["items"][0]["aliases"] == ["alpha", "beta"]
    assert normalized["data"]["items"][1]["aliases"] == ["alpha", "zeta"]
