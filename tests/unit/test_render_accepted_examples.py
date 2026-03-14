from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "render_contract_examples.py"


def _load_generator_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("render_contract_examples", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _spec_by_command(module: ModuleType, command_name: str) -> Any:
    for spec in module.COMMANDS:
        full_name = f"{spec.group} {spec.command}"
        if full_name == command_name:
            return spec
    raise AssertionError(f"Missing spec for {command_name}")


def _example(command: str, label: str, args: dict[str, Any], output: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": label,
        "command": command,
        "purpose": f"Purpose for {label}",
        "args": args,
        "output": output,
    }


def test_render_cli_quotes_values_with_whitespace() -> None:
    module = _load_generator_module()

    cli = module.render_cli(
        "search search-by-eurovoc",
        {"tags": ["financial services"], "since": "2025-01-01", "lang": "eng"},
    )

    assert cli == (
        "cellar search search-by-eurovoc --tags 'financial services' "
        "--since 2025-01-01 --lang eng"
    )


def test_validate_examples_rejects_unknown_commands() -> None:
    module = _load_generator_module()
    specs = [_spec_by_command(module, "lookup resolve-celex")]
    examples = [
        _example(
            "lookup wrong-command",
            "Bad",
            {"celex": "32022R2554"},
            {"ok": True, "data": {"celex": "32022R2554"}},
        )
    ]

    with pytest.raises(ValueError, match="Unknown commands"):
        module.validate_examples(examples, command_specs=specs)


def test_validate_examples_requires_full_command_coverage() -> None:
    module = _load_generator_module()
    specs = [
        _spec_by_command(module, "lookup resolve-celex"),
        _spec_by_command(module, "download get-summary"),
    ]
    examples = [
        _example(
            "lookup resolve-celex",
            "DORA",
            {"celex": "32022R2554"},
            {"ok": True, "data": {"celex": "32022R2554"}},
        )
    ]

    with pytest.raises(ValueError, match="Missing contract examples"):
        module.validate_examples(examples, command_specs=specs)


def test_validate_examples_requires_label_and_purpose() -> None:
    module = _load_generator_module()
    specs = [_spec_by_command(module, "lookup resolve-celex")]
    examples = [
        {
            "label": " ",
            "celex": "32022R2554",
            "command": "lookup resolve-celex",
            "purpose": "Purpose",
            "args": {"celex": "32022R2554"},
            "output": {"ok": True, "data": {"celex": "32022R2554"}},
        }
    ]

    with pytest.raises(ValueError, match="non-empty string `label`"):
        module.validate_examples(examples, command_specs=specs)


def test_validate_examples_allows_null_celex_for_non_celex_commands() -> None:
    module = _load_generator_module()
    specs = [_spec_by_command(module, "search search-by-title")]
    examples = [
        {
            "label": "Search",
            "celex": None,
            "command": "search search-by-title",
            "purpose": "Purpose",
            "args": {"keyword": "banking"},
            "output": {"ok": True, "data": {"items": [], "returned_count": 0}},
        }
    ]

    module.validate_examples(examples, command_specs=specs)


def test_render_markdown_groups_examples_and_preserves_order() -> None:
    module = _load_generator_module()
    specs = [
        _spec_by_command(module, "search search-by-eurovoc"),
        _spec_by_command(module, "download get-summary"),
    ]
    examples = [
        _example(
            "search search-by-eurovoc",
            "First Search",
            {"tags": ["financial services"], "lang": "eng"},
            {"ok": True, "data": {"items": [], "returned_count": 0}},
        ),
        _example(
            "search search-by-eurovoc",
            "Second Search",
            {"tags": ["banking"], "lang": "eng"},
            {"ok": True, "data": {"items": [], "returned_count": 1}},
        ),
        _example(
            "download get-summary",
            "DORA Summary",
            {"celex": "32022R2554", "lang": "eng"},
            {"ok": True, "data": {"language": "eng"}},
        ),
    ]

    rendered = module.render_markdown(examples, command_specs=specs)

    assert "## SEARCH" in rendered
    assert "## DOWNLOAD" in rendered
    assert rendered.index("#### First Search") < rendered.index("#### Second Search")
    assert "### `search search-by-eurovoc`" in rendered
    assert "### `download get-summary`" in rendered


def test_render_markdown_includes_pretty_printed_output_json() -> None:
    module = _load_generator_module()
    specs = [_spec_by_command(module, "lookup resolve-celex")]
    examples = [
        _example(
            "lookup resolve-celex",
            "DORA",
            {"celex": "32022R2554"},
            {"ok": True, "data": {"celex": "32022R2554", "uri": "http://example.test/work"}},
        )
    ]

    rendered = module.render_markdown(examples, command_specs=specs)

    assert "```json" in rendered
    assert '"celex": "32022R2554"' in rendered
    assert '"uri": "http://example.test/work"' in rendered


def test_render_markdown_truncates_large_content_base64_in_docs_output() -> None:
    module = _load_generator_module()
    specs = [_spec_by_command(module, "download get-text")]
    examples = [
        _example(
            "download get-text",
            "DORA XHTML",
            {"celex": "32022R2554", "lang": "eng", "format": "xhtml"},
            {
                "ok": True,
                "data": {
                    "content_base64": "a" * 200,
                    "content_type": "application/xhtml+xml",
                    "language": "eng",
                    "source_url": "http://example.test/text",
                },
            },
        )
    ]

    rendered = module.render_markdown(examples, command_specs=specs)

    assert "[truncated in docs, total length 200]" in rendered
    assert '"content_type": "application/xhtml+xml"' in rendered


def test_repo_accepted_examples_render_successfully() -> None:
    module = _load_generator_module()

    examples = module.load_contract_examples(module.DEFAULT_INPUT_PATH)
    rendered = module.render_markdown(examples)

    assert "## MONITORING" in rendered
    assert "### `download get-text`" in rendered
    assert "### `monitoring new-by-eurovoc`" in rendered


def test_repo_contract_examples_markdown_is_in_sync() -> None:
    module = _load_generator_module()

    examples = module.load_contract_examples(module.DEFAULT_INPUT_PATH)
    rendered = module.render_markdown(examples)
    committed = module.DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8")

    assert rendered == committed
