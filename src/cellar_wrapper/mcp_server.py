"""MCP server adapter for cellar-wrapper."""

from __future__ import annotations

import argparse
import importlib
import os
import sys
from collections.abc import Callable, Mapping
from inspect import Parameter, Signature
from typing import Annotated, Any, Literal, Protocol, cast

from pydantic import BaseModel, ConfigDict, Field, create_model

from cellar_wrapper.cli_policy import build_method_kwargs
from cellar_wrapper.cli_specs import COMMANDS, CommandParameterSpec, CommandSpec
from cellar_wrapper.client import CellarClient
from cellar_wrapper.client_config import build_client_kwargs, validate_finite_positive_float
from cellar_wrapper.constants import MAX_LIMIT
from cellar_wrapper.error_serialization import format_cellar_error
from cellar_wrapper.errors import (
    CellarError,
    CellarInternalError,
    CellarValidationError,
)
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
ToArg = Annotated[str, Field(min_length=1)]
ResourceTypeArg = Annotated[str, Field(pattern=RESOURCE_TYPE_PATTERN)]
ResourceTypeListArg = Annotated[list[ResourceTypeArg], Field(min_length=1)]
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
        value = float(raw)
    except ValueError as exc:
        raise CellarValidationError(f"{key} must be a float: {raw!r}") from exc
    return validate_finite_positive_float(value, field=key)


def _client_kwargs_from_env(env: Mapping[str, str] | None = None) -> dict[str, Any]:
    source = os.environ if env is None else env
    return build_client_kwargs(
        base_url_sparql=_optional_str_env(source, CELLAR_MCP_BASE_URL_SPARQL),
        base_url_resource=_optional_str_env(source, CELLAR_MCP_BASE_URL_RESOURCE),
        user_agent=_optional_str_env(source, CELLAR_MCP_USER_AGENT),
        retries=_optional_int_env(source, CELLAR_MCP_RETRIES),
        timeout_connect=_optional_float_env(source, CELLAR_MCP_TIMEOUT_CONNECT),
        timeout_read=_optional_float_env(source, CELLAR_MCP_TIMEOUT_READ),
        timeout_write=_optional_float_env(source, CELLAR_MCP_TIMEOUT_WRITE),
        timeout_pool=_optional_float_env(source, CELLAR_MCP_TIMEOUT_POOL),
    )


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


def _annotation_for_parameter(param: CommandParameterSpec) -> Any:
    if param.kind == "celex":
        return CelexArg
    if param.kind == "since":
        return SinceArg if param.required else SinceArg | None
    if param.kind == "to":
        return ToArg | None
    if param.kind == "resource_types":
        return ResourceTypeListArg | None
    if param.kind == "country":
        return CountryArg | None
    if param.kind == "lang":
        return LangArg
    if param.kind == "direction":
        return DirectionArg
    if param.kind == "limit":
        return LimitArg
    if param.kind == "offset":
        return OffsetArg
    if param.kind == "format":
        return FormatArg
    if param.kind == "string":
        return NonEmptyStrArg
    if param.kind == "string_list":
        return NonEmptyStrListArg
    raise ValueError(f"Unsupported parameter kind: {param.kind}")


def _signature_for_spec(spec: CommandSpec) -> Signature:
    parameters: list[Parameter] = []
    for param in spec.parameters:
        if param.has_default:
            _append_signature_parameter(
                parameters,
                name=param.name,
                annotation=_annotation_for_parameter(param),
                default=param.default,
            )
            continue
        _append_signature_parameter(
            parameters,
            name=param.name,
            annotation=_annotation_for_parameter(param),
        )

    return Signature(parameters=parameters)


def _tool_description(spec: CommandSpec) -> str:
    return spec.description


def _tool_error(message: str) -> Exception:
    """Build FastMCP ToolError lazily to keep optional dependency optional for typing/import."""
    exceptions_module = importlib.import_module("mcp.server.fastmcp.exceptions")
    tool_error_cls = cast(type[Exception], exceptions_module.ToolError)
    return tool_error_cls(message)


class _StrictArgModelBase(BaseModel):
    """Minimal FastMCP-compatible arg model that forbids unknown fields."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    def model_dump_one_level(self) -> dict[str, Any]:
        return self.model_dump(mode="python")


def _strict_arg_model_for_spec(spec: CommandSpec) -> type[_StrictArgModelBase]:
    model_fields: dict[str, Any] = {}
    for param in spec.parameters:
        annotation = _annotation_for_parameter(param)
        if param.has_default:
            model_fields[param.name] = (annotation, param.default)
            continue
        model_fields[param.name] = annotation
    return create_model(
        f"{spec.method}Arguments",
        __base__=_StrictArgModelBase,
        **model_fields,
    )


def _replace_tool_arg_model(server: MCPServer, spec: CommandSpec) -> None:
    """Replace FastMCP's permissive arg model with an explicit strict model."""
    tool_manager = getattr(server, "_tool_manager", None)
    if tool_manager is None:
        return
    get_tool = getattr(tool_manager, "get_tool", None)
    if not callable(get_tool):
        return
    tool = get_tool(spec.command)
    if tool is None:
        return
    fn_metadata = getattr(tool, "fn_metadata", None)
    if fn_metadata is None:
        return
    arg_model = _strict_arg_model_for_spec(spec)
    fn_metadata.arg_model = arg_model
    tool.parameters = arg_model.model_json_schema(by_alias=True)


def _tool_for_spec(spec: CommandSpec, client_factory: Callable[[], CellarClient]) -> Callable[..., Any]:
    signature = _signature_for_spec(spec)

    def tool(**tool_args: Any) -> Any:
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
        _replace_tool_arg_model(server, spec)
    return server


def build_main_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cellar-mcp")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _main_argv(argv: list[str] | None) -> list[str]:
    if argv is not None:
        return argv
    return sys.argv[1:] if sys.argv[1:] == ["--version"] else []


def main(argv: list[str] | None = None) -> None:
    parser = build_main_parser()
    parser.parse_args(_main_argv(argv))

    try:
        server = build_mcp_server()
    except CellarValidationError as exc:
        raise SystemExit(f"Invalid MCP configuration: {exc}") from exc
    server.run("stdio")


if __name__ == "__main__":
    main(sys.argv[1:])
