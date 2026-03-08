from __future__ import annotations

import importlib
import json
from types import TracebackType
from typing import Any, cast

import anyio
import pytest

from cellar_wrapper.cli_specs import COMMANDS, CommandSpec
from cellar_wrapper.constants import DEFAULT_LANGUAGE, DEFAULT_LIMIT, DEFAULT_OFFSET
from cellar_wrapper.errors import CellarHTTPError, CellarValidationError
from cellar_wrapper.http import TimeoutConfig
from cellar_wrapper.mcp_server import (
    CELLAR_MCP_BASE_URL_RESOURCE,
    CELLAR_MCP_BASE_URL_SPARQL,
    CELLAR_MCP_RETRIES,
    CELLAR_MCP_TIMEOUT_CONNECT,
    CELLAR_MCP_TIMEOUT_POOL,
    CELLAR_MCP_TIMEOUT_READ,
    CELLAR_MCP_TIMEOUT_WRITE,
    CELLAR_MCP_USER_AGENT,
    _client_kwargs_from_env,
    build_mcp_server,
    main,
)
from cellar_wrapper.version import __version__


def _list_tools(server: Any) -> list[Any]:
    async def run() -> list[Any]:
        return cast(list[Any], await server.list_tools())

    return anyio.run(run)


def _call_tool(server: Any, name: str, arguments: dict[str, Any]) -> Any:
    async def run() -> Any:
        return await server.call_tool(name, arguments)

    return anyio.run(run)


def _tool_error_type() -> type[BaseException]:
    exceptions_module = pytest.importorskip("mcp.server.fastmcp.exceptions")
    return cast(type[BaseException], exceptions_module.ToolError)


def _require_mcp_sdk() -> None:
    pytest.importorskip("mcp.server.fastmcp")


def _tool_call_payload(result: Any) -> dict[str, Any]:
    if isinstance(result, tuple):
        payload = result[1]
        assert isinstance(payload, dict)
        return payload

    assert isinstance(result, list)
    assert result
    assert isinstance(result[0].text, str)
    payload = json.loads(result[0].text)
    assert isinstance(payload, dict)
    return payload


def _expected_schema_contract(
    spec: CommandSpec,
) -> tuple[set[str], set[str], dict[str, Any], set[str]]:
    properties: set[str] = set()
    required: set[str] = set()
    defaults: dict[str, Any] = {}
    without_default: set[str] = set()

    def add_required(name: str) -> None:
        properties.add(name)
        required.add(name)
        without_default.add(name)

    def add_default(name: str, value: Any) -> None:
        properties.add(name)
        defaults[name] = value

    if spec.requires_celex:
        add_required("celex")

    if spec.requires_since:
        add_required("since")
    elif spec.has_since:
        add_default("since", None)

    if spec.has_resource_type:
        add_default("resource_type", None)
    if spec.has_country:
        add_default("country", None)
    if spec.has_lang:
        add_default("lang", DEFAULT_LANGUAGE)
    if spec.has_limit_offset:
        add_default("limit", DEFAULT_LIMIT)
        add_default("offset", DEFAULT_OFFSET)
    if spec.has_format:
        add_default("format", "pdf")
    if spec.list_arg_name is not None:
        add_required(spec.list_arg_name)
    if spec.scalar_arg_name is not None:
        add_required(spec.scalar_arg_name)

    return properties, required, defaults, without_default


def _tool_error_details(message: str) -> dict[str, Any]:
    marker = "| details="
    assert marker in message
    payload = json.loads(message.split(marker, maxsplit=1)[1])
    assert isinstance(payload, dict)
    return payload


def test_mcp_registers_all_command_specs() -> None:
    _require_mcp_sdk()
    server = build_mcp_server()
    tools = _list_tools(server)

    assert len(tools) == len(COMMANDS)
    assert {tool.name for tool in tools} == {spec.command for spec in COMMANDS}


def test_mcp_tool_schemas_cover_all_commands() -> None:
    _require_mcp_sdk()
    server = build_mcp_server()
    tools = {tool.name: tool for tool in _list_tools(server)}

    for spec in COMMANDS:
        schema = tools[spec.command].inputSchema
        expected_properties, expected_required, expected_defaults, expected_without_default = (
            _expected_schema_contract(spec)
        )

        properties = schema["properties"]
        assert schema["type"] == "object"
        assert schema.get("additionalProperties") is False
        assert set(properties) == expected_properties
        assert set(schema.get("required", [])) == expected_required

        defaults_in_schema = {name for name, property_schema in properties.items() if "default" in property_schema}
        assert defaults_in_schema == set(expected_defaults)

        for name, expected_value in expected_defaults.items():
            assert properties[name]["default"] == expected_value

        for name in expected_without_default:
            assert "default" not in properties[name]


def test_mcp_regressed_commands_expose_resource_type_in_schema() -> None:
    _require_mcp_sdk()
    server = build_mcp_server()
    tools = {tool.name: tool for tool in _list_tools(server)}

    for command_name in (
        "get-cjeu-judgments",
        "get-preliminary-questions",
        "new-case-law",
        "new-preliminary-questions",
        "new-corrigenda",
        "new-consolidated",
        "new-nims",
    ):
        properties = tools[command_name].inputSchema["properties"]
        assert "resource_type" in properties
        assert properties["resource_type"]["default"] is None


def test_mcp_tool_dispatch_maps_kwargs_correctly(monkeypatch: pytest.MonkeyPatch) -> None:
    _require_mcp_sdk()
    calls: list[dict[str, Any]] = []

    class RecordingClient:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs

        def __enter__(self) -> RecordingClient:
            return self

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> None:
            return None

        def get_amendments(self, **kwargs: Any) -> dict[str, Any]:
            calls.append(kwargs)
            return {"kwargs": kwargs}

    monkeypatch.setattr("cellar_wrapper.mcp_server.CellarClient", RecordingClient)

    server = build_mcp_server()
    structured_payload = _tool_call_payload(_call_tool(server, "get-amendments", {"celex": "32022R2554"}))

    assert calls
    assert calls[0] == {
        "celex": "32022R2554",
        "resource_type": None,
        "lang": "eng",
        "limit": 200,
        "offset": 0,
    }
    assert structured_payload["kwargs"]["celex"] == "32022R2554"


def test_mcp_domain_errors_raise_tool_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _require_mcp_sdk()
    class ErrorClient:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs

        def __enter__(self) -> ErrorClient:
            return self

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> None:
            return None

        def resolve_celex(self, celex: str) -> dict[str, str]:
            raise CellarValidationError(f"bad celex: {celex}")

    monkeypatch.setattr("cellar_wrapper.mcp_server.CellarClient", ErrorClient)

    server = build_mcp_server()
    with pytest.raises(_tool_error_type()) as exc_info:
        _call_tool(server, "resolve-celex", {"celex": "32022R2554"})
    message = str(exc_info.value)
    assert "CellarValidationError" in message
    assert "bad celex: 32022R2554" in message
    assert "| details=" not in message


def test_mcp_unexpected_errors_raise_internal_tool_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _require_mcp_sdk()
    class ErrorClient:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs

        def __enter__(self) -> ErrorClient:
            return self

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> None:
            return None

        def resolve_celex(self, celex: str) -> dict[str, str]:
            raise RuntimeError(f"boom: {celex}")

    monkeypatch.setattr("cellar_wrapper.mcp_server.CellarClient", ErrorClient)

    server = build_mcp_server()
    with pytest.raises(_tool_error_type()) as exc_info:
        _call_tool(server, "resolve-celex", {"celex": "32022R2554"})

    message = str(exc_info.value)
    assert "CellarInternalError" in message
    assert "Unexpected internal error" in message
    details = _tool_error_details(message)
    assert details == {"original_type": "RuntimeError"}


def test_mcp_unknown_args_raise_tool_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _require_mcp_sdk()
    calls: list[dict[str, Any]] = []

    class RecordingClient:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs

        def __enter__(self) -> RecordingClient:
            return self

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> None:
            return None

        def resolve_celex(self, celex: str) -> dict[str, str]:
            calls.append({"celex": celex})
            return {"celex": celex}

    monkeypatch.setattr("cellar_wrapper.mcp_server.CellarClient", RecordingClient)

    server = build_mcp_server()
    with pytest.raises(_tool_error_type()) as exc_info:
        _call_tool(
            server,
            "resolve-celex",
            {"celex": "32022R2554", "unexpected": "ignored-no-more"},
        )
    assert not calls

    lowered_message = str(exc_info.value).lower()
    assert any(
        token in lowered_message
        for token in (
            "unknown",
            "unexpected",
            "extra",
            "forbidden",
        )
    )


def test_mcp_domain_errors_include_json_safe_details(monkeypatch: pytest.MonkeyPatch) -> None:
    _require_mcp_sdk()
    class DeterministicOpaqueValue:
        def __repr__(self) -> str:
            return "<deterministic-opaque>"

    class ErrorClient:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs

        def __enter__(self) -> ErrorClient:
            return self

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> None:
            return None

        def resolve_celex(self, celex: str) -> dict[str, str]:
            raise CellarHTTPError(
                "upstream failed",
                status_code=502,
                url="https://example.test/sparql",
                body_excerpt="bad gateway",
                details={"attempt": 3, "opaque": DeterministicOpaqueValue()},
            )

    monkeypatch.setattr("cellar_wrapper.mcp_server.CellarClient", ErrorClient)

    server = build_mcp_server()
    with pytest.raises(_tool_error_type()) as exc_info:
        _call_tool(server, "resolve-celex", {"celex": "32022R2554"})

    message = str(exc_info.value)
    details = _tool_error_details(message)
    assert "CellarHTTPError" in message
    assert details == {
        "body_excerpt": "bad gateway",
        "details": {"attempt": 3, "opaque": "<deterministic-opaque>"},
        "status_code": 502,
        "url": "https://example.test/sparql",
    }


def test_client_kwargs_from_env_uses_runtime_overrides() -> None:
    env = {
        CELLAR_MCP_BASE_URL_SPARQL: "https://example.test/sparql",
        CELLAR_MCP_BASE_URL_RESOURCE: "https://example.test/resource",
        CELLAR_MCP_USER_AGENT: "mcp-test/1.0",
        CELLAR_MCP_RETRIES: "7",
        CELLAR_MCP_TIMEOUT_CONNECT: "1.5",
        CELLAR_MCP_TIMEOUT_READ: "2.5",
        CELLAR_MCP_TIMEOUT_WRITE: "3.5",
        CELLAR_MCP_TIMEOUT_POOL: "4.5",
    }
    kwargs = _client_kwargs_from_env(env)

    assert kwargs["base_url_sparql"] == "https://example.test/sparql"
    assert kwargs["base_url_resource"] == "https://example.test/resource"
    assert kwargs["user_agent"] == "mcp-test/1.0"
    assert kwargs["retries"] == 7

    timeout = kwargs["timeout"]
    assert isinstance(timeout, TimeoutConfig)
    assert timeout.connect == 1.5
    assert timeout.read == 2.5
    assert timeout.write == 3.5
    assert timeout.pool == 4.5


def test_client_kwargs_from_env_rejects_invalid_numbers() -> None:
    with pytest.raises(CellarValidationError, match=CELLAR_MCP_RETRIES):
        _client_kwargs_from_env({CELLAR_MCP_RETRIES: "not-an-int"})


def test_main_exits_with_install_hint_when_mcp_dependency_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import = importlib.import_module

    def fake_import(name: str, package: str | None = None) -> Any:
        if name == "mcp.server.fastmcp":
            raise ModuleNotFoundError("No module named 'mcp'")
        return real_import(name, package)

    monkeypatch.setattr("cellar_wrapper.mcp_server.importlib.import_module", fake_import)

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert "cellar-wrapper[mcp]" in str(exc_info.value)


def test_main_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    assert capsys.readouterr().out.strip() == f"cellar-mcp {__version__}"
