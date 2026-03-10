"""MCP server adapter for cellar-wrapper."""

from __future__ import annotations

import argparse
import importlib
import os
from collections.abc import Callable, Mapping
from inspect import Parameter, Signature
from typing import Annotated, Any, Literal, Protocol, cast

from pydantic import Field

from cellar_wrapper.cli_policy import build_method_kwargs
from cellar_wrapper.cli_specs import COMMANDS, CommandSpec
from cellar_wrapper.client import CellarClient
from cellar_wrapper.constants import DEFAULT_LANGUAGE, DEFAULT_LIMIT, DEFAULT_OFFSET, MAX_LIMIT
from cellar_wrapper.error_serialization import format_cellar_error
from cellar_wrapper.errors import (
    CellarError,
    CellarInternalError,
    CellarValidationError,
)
from cellar_wrapper.http import TimeoutConfig, validate_http_url
from cellar_wrapper.serialization import to_jsonable
from cellar_wrapper.version import __version__

CELLAR_MCP_BASE_URL_SPARQL = "CELLAR_MCP_BASE_URL_SPARQL"
CELLAR_MCP_BASE_URL_RESOURCE = "CELLAR_MCP_BASE_URL_RESOURCE"
CELLAR_MCP_USER_AGENT = "CELLAR_MCP_USER_AGENT"
CELLAR_MCP_RETRIES = "CELLAR_MCP_RETRIES"
CELLAR_MCP_TIMEOUT_CONNECT = "CELLAR_MCP_TIMEOUT_CONNECT"
CELLAR_MCP_TIMEOUT_READ = "CELLAR_MCP_TIMEOUT_READ"
CELLAR_MCP_TIMEOUT_WRITE = "CELLAR_MCP_TIMEOUT_WRITE"
CELLAR_MCP_TIMEOUT_POOL = "CELLAR_MCP_TIMEOUT_POOL"

CELEX_PATTERN = r"^[0-9A-Z()_\-]{5,40}$"
LANG_PATTERN = r"^[a-zA-Z]{3}$"
RESOURCE_TYPE_PATTERN = r"^[A-Z_]+$"
COUNTRY_PATTERN = r"^[A-Z]{3}$"

CelexArg = Annotated[str, Field(pattern=CELEX_PATTERN)]
SinceArg = Annotated[str, Field(min_length=1)]
ResourceTypeArg = Annotated[str, Field(pattern=RESOURCE_TYPE_PATTERN)]
CountryArg = Annotated[str, Field(pattern=COUNTRY_PATTERN)]
LangArg = Annotated[str, Field(pattern=LANG_PATTERN)]
DirectionArg = Literal["incoming", "outgoing", "both"]
LimitArg = Annotated[int, Field(ge=1, le=MAX_LIMIT)]
OffsetArg = Annotated[int, Field(ge=0)]
NonEmptyStrArg = Annotated[str, Field(min_length=1)]
NonEmptyStrListArg = Annotated[list[NonEmptyStrArg], Field(min_length=1)]
FormatArg = Literal["pdf", "xhtml", "xml", "rdf", "docx"]


class MCPServer(Protocol):
    """Minimal MCP server protocol used by this module."""

    def add_tool(
        self,
        fn: Callable[..., Any],
        name: str | None = None,
        description: str | None = None,
    ) -> None: ...

    def run(self, transport: str = "stdio", mount_path: str | None = None) -> None: ...


FastMCPFactory = Callable[..., MCPServer]


def _resolve_fastmcp_factory() -> FastMCPFactory:
    try:
        module = importlib.import_module("mcp.server.fastmcp")
    except ModuleNotFoundError as exc:  # pragma: no cover - exercised via integration test
        raise SystemExit(
            'MCP support requires optional dependency. Install with: '
            'pip install "cellar-wrapper[mcp]"'
        ) from exc

    fast_mcp = getattr(module, "FastMCP", None)
    if fast_mcp is None:  # pragma: no cover - defensive guard
        raise SystemExit("MCP SDK is installed, but FastMCP is unavailable.")

    return cast(FastMCPFactory, fast_mcp)


def _optional_str_env(env: Mapping[str, str], key: str) -> str | None:
    raw = env.get(key)
    if raw is None:
        return None
    value = raw.strip()
    if not value:
        raise CellarValidationError(f"{key} cannot be empty when set")
    return value


def _optional_int_env(env: Mapping[str, str], key: str) -> int | None:
    raw = _optional_str_env(env, key)
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError as exc:
        raise CellarValidationError(f"{key} must be an integer: {raw!r}") from exc


def _optional_float_env(env: Mapping[str, str], key: str) -> float | None:
    raw = _optional_str_env(env, key)
    if raw is None:
        return None
    try:
        return float(raw)
    except ValueError as exc:
        raise CellarValidationError(f"{key} must be a float: {raw!r}") from exc


def _timeout_from_env(env: Mapping[str, str]) -> TimeoutConfig | None:
    connect = _optional_float_env(env, CELLAR_MCP_TIMEOUT_CONNECT)
    read = _optional_float_env(env, CELLAR_MCP_TIMEOUT_READ)
    write = _optional_float_env(env, CELLAR_MCP_TIMEOUT_WRITE)
    pool = _optional_float_env(env, CELLAR_MCP_TIMEOUT_POOL)

    if connect is None and read is None and write is None and pool is None:
        return None

    defaults = TimeoutConfig()
    return TimeoutConfig(
        connect=connect if connect is not None else defaults.connect,
        read=read if read is not None else defaults.read,
        write=write if write is not None else defaults.write,
        pool=pool if pool is not None else defaults.pool,
    )


def _client_kwargs_from_env(env: Mapping[str, str] | None = None) -> dict[str, Any]:
    source = os.environ if env is None else env
    kwargs: dict[str, Any] = {}

    base_url_sparql = _optional_str_env(source, CELLAR_MCP_BASE_URL_SPARQL)
    if base_url_sparql is not None:
        kwargs["base_url_sparql"] = validate_http_url(
            base_url_sparql,
            field=CELLAR_MCP_BASE_URL_SPARQL,
        )

    base_url_resource = _optional_str_env(source, CELLAR_MCP_BASE_URL_RESOURCE)
    if base_url_resource is not None:
        kwargs["base_url_resource"] = validate_http_url(
            base_url_resource,
            field=CELLAR_MCP_BASE_URL_RESOURCE,
        )

    user_agent = _optional_str_env(source, CELLAR_MCP_USER_AGENT)
    if user_agent is not None:
        kwargs["user_agent"] = user_agent

    retries = _optional_int_env(source, CELLAR_MCP_RETRIES)
    if retries is not None:
        if retries < 1:
            raise CellarValidationError(f"{CELLAR_MCP_RETRIES} must be >= 1")
        kwargs["retries"] = retries

    timeout = _timeout_from_env(source)
    if timeout is not None:
        kwargs["timeout"] = timeout

    return kwargs


_NO_DEFAULT = object()


def _append_signature_parameter(
    parameters: list[Parameter],
    *,
    name: str,
    annotation: Any,
    default: Any = _NO_DEFAULT,
) -> None:
    kwargs: dict[str, Any] = {}
    if default is not _NO_DEFAULT:
        kwargs["default"] = default
    parameters.append(
        Parameter(
            name,
            kind=Parameter.KEYWORD_ONLY,
            annotation=annotation,
            **kwargs,
        )
    )


def _add_optional_signature_parameters(parameters: list[Parameter], spec: CommandSpec) -> None:
    optional_specs: tuple[tuple[bool, str, Any, Any], ...] = (
        (spec.has_resource_type, "resource_type", ResourceTypeArg | None, None),
        (spec.has_country, "country", CountryArg | None, None),
        (spec.has_lang, "lang", LangArg, DEFAULT_LANGUAGE),
        (spec.has_direction, "direction", DirectionArg, "both"),
        (spec.has_limit_offset, "limit", LimitArg, DEFAULT_LIMIT),
        (spec.has_limit_offset, "offset", OffsetArg, DEFAULT_OFFSET),
        (spec.has_format, "format", FormatArg, "pdf"),
    )
    for enabled, name, annotation, default in optional_specs:
        if not enabled:
            continue
        _append_signature_parameter(
            parameters,
            name=name,
            annotation=annotation,
            default=default,
        )


def _signature_for_spec(spec: CommandSpec) -> Signature:
    parameters: list[Parameter] = []

    if spec.requires_celex:
        _append_signature_parameter(parameters, name="celex", annotation=CelexArg)

    if spec.requires_since:
        _append_signature_parameter(parameters, name="since", annotation=SinceArg)
    elif spec.has_since:
        _append_signature_parameter(
            parameters,
            name="since",
            annotation=SinceArg | None,
            default=None,
        )

    _add_optional_signature_parameters(parameters, spec)

    if spec.list_arg_name is not None:
        _append_signature_parameter(
            parameters,
            name=spec.list_arg_name,
            annotation=NonEmptyStrListArg,
        )

    if spec.scalar_arg_name is not None:
        _append_signature_parameter(
            parameters,
            name=spec.scalar_arg_name,
            annotation=NonEmptyStrArg,
        )

    return Signature(parameters=parameters)


def _tool_description(spec: CommandSpec) -> str:
    return (
        f"CELLAR command '{spec.group} {spec.command}' "
        f"mapped to CellarClient.{spec.method}."
    )


def _tool_error(message: str) -> Exception:
    """Build FastMCP ToolError lazily to keep optional dependency optional for typing/import."""
    exceptions_module = importlib.import_module("mcp.server.fastmcp.exceptions")
    tool_error_cls = cast(type[Exception], exceptions_module.ToolError)
    return tool_error_cls(message)


def _enforce_strict_tool_arguments(server: MCPServer, tool_name: str) -> None:
    """Force FastMCP arg model to reject unknown parameters."""
    tool_manager = getattr(server, "_tool_manager", None)
    if tool_manager is None:
        return
    get_tool = getattr(tool_manager, "get_tool", None)
    if not callable(get_tool):
        return
    tool = get_tool(tool_name)
    if tool is None:
        return

    arg_model = getattr(getattr(tool, "fn_metadata", None), "arg_model", None)
    if arg_model is None:
        return
    model_config = getattr(arg_model, "model_config", None)
    if model_config is None:
        return

    model_config["extra"] = "forbid"
    arg_model.model_rebuild(force=True)
    tool.parameters = arg_model.model_json_schema(by_alias=True)


def _tool_for_spec(spec: CommandSpec, client_factory: Callable[[], CellarClient]) -> Callable[..., Any]:
    signature = _signature_for_spec(spec)
    allowed_args = set(signature.parameters.keys())

    def tool(**tool_args: Any) -> Any:
        unknown_args = sorted(set(tool_args) - allowed_args)
        if unknown_args:
            unknown_args_csv = ", ".join(unknown_args)
            raise _tool_error(
                f"Invalid parameters for tool '{spec.command}': {unknown_args_csv}"
            )

        namespace = argparse.Namespace(**tool_args)
        method_kwargs = build_method_kwargs(spec, namespace)

        try:
            with client_factory() as client:
                method = getattr(client, spec.method)
                return to_jsonable(method(**method_kwargs))
        except CellarError as exc:
            raise _tool_error(format_cellar_error(exc)) from exc
        except Exception as exc:  # pragma: no cover - guarded via integration test
            internal_error = CellarInternalError(
                "Unexpected internal error",
                details={"original_type": type(exc).__name__},
            )
            raise _tool_error(format_cellar_error(internal_error)) from exc

    tool.__name__ = f"tool_{spec.method}"
    tool.__qualname__ = tool.__name__
    tool.__doc__ = _tool_description(spec)
    cast(Any, tool).__signature__ = signature
    return tool


def _default_client_factory(env: Mapping[str, str] | None = None) -> Callable[[], CellarClient]:
    client_kwargs = _client_kwargs_from_env(env)

    def factory() -> CellarClient:
        return CellarClient(**client_kwargs)

    return factory


def build_mcp_server(
    *,
    env: Mapping[str, str] | None = None,
    client_factory: Callable[[], CellarClient] | None = None,
    fastmcp_factory: FastMCPFactory | None = None,
) -> MCPServer:
    resolved_factory = fastmcp_factory or _resolve_fastmcp_factory()
    resolved_client_factory = client_factory or _default_client_factory(env)

    server = resolved_factory(name="cellar-wrapper")
    for spec in COMMANDS:
        server.add_tool(
            _tool_for_spec(spec, resolved_client_factory),
            name=spec.command,
            description=_tool_description(spec),
        )
        _enforce_strict_tool_arguments(server, spec.command)
    return server


def build_main_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cellar-mcp")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_main_parser()
    parser.parse_args([] if argv is None else argv)

    try:
        server = build_mcp_server()
    except CellarValidationError as exc:
        raise SystemExit(f"Invalid MCP configuration: {exc}") from exc
    server.run("stdio")


if __name__ == "__main__":
    main()
