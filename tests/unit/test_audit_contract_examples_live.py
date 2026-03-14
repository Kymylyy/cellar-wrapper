from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, cast

import cellar_wrapper.contract_examples as contract_examples

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


def _example(command: str, label: str) -> dict[str, Any]:
    return {
        "label": label,
        "celex": "32022R2554",
        "command": command,
        "purpose": f"Purpose for {label}",
        "args": {"celex": "32022R2554"},
        "output": {
            "ok": True,
            "data": {
                "label": label,
            },
        },
    }


def test_normalize_payload_removes_volatile_timestamps() -> None:
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

    normalized = contract_examples.normalize_payload(payload)

    assert "executed_at" not in normalized["data"]["meta"]
    assert normalized["data"]["meta"]["limit"] == 5


def test_normalize_payload_sorts_data_items_for_order_insensitive_audit() -> None:
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

    normalized = contract_examples.normalize_payload(payload)

    assert [item["uri"] for item in normalized["data"]["items"]] == [
        "http://example.test/a",
        "http://example.test/b",
    ]
    assert normalized["data"]["items"][0]["aliases"] == ["alpha", "beta"]
    assert normalized["data"]["items"][1]["aliases"] == ["alpha", "zeta"]


def test_select_audit_examples_smoke_uses_fixed_subset_keys() -> None:
    examples = [
        _example("lookup resolve-celex", "DORA"),
        _example("lookup get-act", "MiCA"),
        _example("lookup get-act", "MiCA"),
        _example("relations get-amendments", "PSR"),
        _example("lifecycle get-consolidated-versions", "PSD2"),
        _example("case-law get-cjeu-judgments", "PSD2"),
        _example("search search-by-title", "Crypto-assets"),
        _example("search search-by-title", "Crypto-assets"),
        _example("monitoring new-citations", "MiCA"),
        _example("monitoring new-citations", "MiCA"),
        _example("download get-summary", "DORA"),
        _example("lookup get-act", "FiDAR"),
    ]

    selected = contract_examples.select_audit_examples(examples, smoke=True)

    assert [(ref.command, ref.label) for ref in selected] == list(contract_examples.SMOKE_EXAMPLE_KEYS)


def test_select_audit_examples_filters_intersect_and_limit_applies_last() -> None:
    examples = [
        _example("lookup get-act", "MiCA"),
        _example("lookup get-act", "FiDAR"),
        _example("lookup resolve-celex", "DORA"),
        _example("download get-summary", "DORA"),
    ]

    selected = contract_examples.select_audit_examples(
        examples,
        command_filter=["lookup get-act", "download get-summary"],
        group_filter=["lookup"],
        label_filter=["MiCA", "DORA"],
        limit=1,
    )

    assert [(ref.command, ref.label) for ref in selected] == [("lookup get-act", "MiCA")]


def test_audit_examples_live_detailed_reports_timeout_and_fail_fast(
    monkeypatch: Any,
) -> None:
    examples = [
        _example("lookup get-act", "MiCA"),
        _example("download get-summary", "DORA"),
    ]
    seen_labels: list[str] = []
    progress_lines: list[str] = []
    result_lines: list[str] = []

    monkeypatch.setattr(contract_examples, "build_cli_env", lambda: {})
    monkeypatch.setattr(
        contract_examples,
        "build_cli_argv",
        lambda example: ["cellar-audit", str(example["label"])],
    )

    def fake_run(
        argv: list[str],
        *,
        cwd: Path,
        env: dict[str, str],
        capture_output: bool,
        text: bool,
        check: bool,
        timeout: float | None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, env, capture_output, text, check
        label = argv[1]
        seen_labels.append(label)
        raise subprocess.TimeoutExpired(argv, timeout)

    monkeypatch.setattr(contract_examples.subprocess, "run", fake_run)

    run = contract_examples.audit_examples_live_detailed(
        examples,
        options=contract_examples.ContractExamplesAuditOptions(
            timeout_seconds=7,
            slow_threshold_seconds=1,
            fail_fast=True,
        ),
        progress_handler=progress_lines.append,
        result_handler=result_lines.append,
    )

    assert seen_labels == ["MiCA"]
    assert progress_lines == ["[1/2] RUN lookup get-act [MiCA]"]
    assert len(run.records) == 1
    assert run.records[0].status == "timeout"
    assert result_lines[0].startswith("[1/2] TIMEOUT")


def test_audit_examples_live_renders_failures_with_cli_and_summary(
    monkeypatch: Any,
) -> None:
    examples = [_example("lookup get-act", "MiCA")]

    monkeypatch.setattr(contract_examples, "build_cli_env", lambda: {})
    monkeypatch.setattr(
        contract_examples,
        "build_cli_argv",
        lambda example: ["cellar-audit", str(example["label"])],
    )

    def fake_run(
        argv: list[str],
        *,
        cwd: Path,
        env: dict[str, str],
        capture_output: bool,
        text: bool,
        check: bool,
        timeout: float | None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, env, capture_output, text, check, timeout
        return subprocess.CompletedProcess(argv, 2, stdout="", stderr="boom")

    monkeypatch.setattr(contract_examples.subprocess, "run", fake_run)

    failures = contract_examples.audit_examples_live(examples, fail_fast=True)

    assert failures
    assert "Audit failures:" in failures[0]
    assert "CLI: cellar lookup get-act --celex 32022R2554" in failures[1]
    assert "CLI exited with 2" in failures[1]


def test_wrapper_main_builds_options_and_uses_detailed_engine(
    monkeypatch: Any,
    capsys: Any,
) -> None:
    module = _load_audit_module()
    examples = [_example("lookup get-act", "MiCA")]
    captured: dict[str, Any] = {}

    def fake_audit_examples_live_detailed(
        loaded_examples: list[dict[str, Any]],
        *,
        options: contract_examples.ContractExamplesAuditOptions,
        progress_handler: Any,
        result_handler: Any,
        env: Any = None,
    ) -> contract_examples.ContractExamplesAuditRun:
        del progress_handler, result_handler, env
        captured["examples"] = loaded_examples
        captured["options"] = options
        return contract_examples.ContractExamplesAuditRun(
            options=options,
            total_examples=len(loaded_examples),
            selected_examples=[
                contract_examples.AuditExampleRef(
                    index=1,
                    command="lookup get-act",
                    group="lookup",
                    label="MiCA",
                    cli="cellar lookup get-act --celex 32022R2554",
                    example=loaded_examples[0],
                )
            ],
            records=[],
        )

    monkeypatch.setattr(
        module,
        "contract_examples",
        SimpleNamespace(
            DEFAULT_INPUT_PATH=ROOT / "docs" / "examples" / "contract-examples.json",
            ContractExamplesAuditOptions=contract_examples.ContractExamplesAuditOptions,
            ContractExamplesAuditRun=contract_examples.ContractExamplesAuditRun,
            AuditExampleRef=contract_examples.AuditExampleRef,
            normalize_payload=contract_examples.normalize_payload,
            load_contract_examples=lambda path: examples,
            audit_examples_live_detailed=fake_audit_examples_live_detailed,
            render_audit_summary=lambda run: ["Audit summary:", "- selected: 1 of 1"],
            render_audit_failures=lambda run: [],
        ),
    )

    main = cast(Any, module.main)
    result = main(
        [
            "--mode",
            "smoke",
            "--command",
            "lookup get-act",
            "--group",
            "lookup",
            "--label",
            "MiCA",
            "--limit",
            "2",
            "--timeout-seconds",
            "9",
            "--slow-threshold-seconds",
            "4",
            "--fail-fast",
        ]
    )

    assert result == 0
    assert captured["examples"] == examples
    assert captured["options"] == contract_examples.ContractExamplesAuditOptions(
        smoke=True,
        command_filter=frozenset({"lookup get-act"}),
        group_filter=frozenset({"lookup"}),
        label_filter=frozenset({"MiCA"}),
        limit=2,
        timeout_seconds=9.0,
        slow_threshold_seconds=4.0,
        fail_fast=True,
    )
    stdout, stderr = capsys.readouterr()
    assert "Live audit matched 1 curated contract examples (mode=smoke)." in stdout
    assert "Audit summary:" in stderr
