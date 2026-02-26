"""Command-line interface for CELLAR wrapper."""

from __future__ import annotations

import argparse
import json
from typing import Any, NoReturn

from pydantic import BaseModel

from cellar_wrapper.cli_specs import COMMANDS, CommandSpec
from cellar_wrapper.client import CellarClient
from cellar_wrapper.constants import DEFAULT_LANGUAGE, DEFAULT_LIMIT, DEFAULT_OFFSET
from cellar_wrapper.errors import (
    CellarError,
    CellarHTTPError,
    CellarRateLimitError,
    CellarSPARQLError,
    CellarValidationError,
)
from cellar_wrapper.http import TimeoutConfig
from cellar_wrapper.models import ErrorPayload


class JsonArgumentParser(argparse.ArgumentParser):
    """ArgumentParser variant that surfaces validation errors as exceptions."""

    def error(self, message: str) -> NoReturn:  # pragma: no cover - exercised via run()
        raise CellarValidationError(message)


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    return value


def _emit_success(data: Any) -> int:
    payload = {"ok": True, "data": _to_jsonable(data)}
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def _emit_error(exc: Exception) -> int:
    details: dict[str, Any] = {}
    if isinstance(exc, CellarHTTPError):
        details = {
            "status_code": exc.status_code,
            "url": exc.url,
            "body_excerpt": exc.body_excerpt,
            "details": exc.details,
        }
        if isinstance(exc, CellarRateLimitError):
            details["retry_after"] = exc.retry_after
            details["retry_after_seconds"] = exc.retry_after_seconds
    elif isinstance(exc, CellarSPARQLError):
        details = {
            "query": exc.query,
            "response_excerpt": exc.response_excerpt,
            "details": exc.details,
        }

    error = ErrorPayload(type=type(exc).__name__, message=str(exc), details=details)
    payload = {"ok": False, "error": error.model_dump(mode="json")}
    print(json.dumps(payload, ensure_ascii=False))
    return 1


def _positive_int(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if value < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return value


def _add_global_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--base-url-sparql", default=None)
    parser.add_argument("--base-url-resource", default=None)
    parser.add_argument("--retries", type=_positive_int, default=None)
    parser.add_argument("--timeout-connect", type=float, default=None)
    parser.add_argument("--timeout-read", type=float, default=None)
    parser.add_argument("--timeout-write", type=float, default=None)
    parser.add_argument("--timeout-pool", type=float, default=None)


def _configure_command_parser(command_parser: argparse.ArgumentParser, spec: CommandSpec) -> None:
    command_parser.set_defaults(command_spec=spec)

    if spec.requires_celex:
        command_parser.add_argument("--celex", required=True)
    if spec.requires_since:
        command_parser.add_argument("--since", required=True)
    elif spec.has_since:
        command_parser.add_argument("--since")

    if spec.has_resource_type:
        command_parser.add_argument("--resource-type")
    if spec.has_lang:
        command_parser.add_argument("--lang", default=DEFAULT_LANGUAGE)
    if spec.has_limit_offset:
        command_parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
        command_parser.add_argument("--offset", type=int, default=DEFAULT_OFFSET)
    if spec.has_format:
        command_parser.add_argument("--format", default="pdf")
    if spec.list_arg_name is not None:
        command_parser.add_argument(f"--{spec.list_arg_name}", nargs="+", required=True)
    if spec.scalar_arg_name is not None:
        command_parser.add_argument(f"--{spec.scalar_arg_name}", required=True)


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(prog="cellar")
    _add_global_args(parser)

    group_subparsers = parser.add_subparsers(dest="group", required=True)
    command_subparsers_by_group: dict[str, Any] = {}

    for spec in COMMANDS:
        if spec.group not in command_subparsers_by_group:
            group_parser = group_subparsers.add_parser(spec.group)
            group_parser.set_defaults(group_name=spec.group)
            command_subparsers_by_group[spec.group] = group_parser.add_subparsers(
                dest="command", required=True
            )

        command_parser = command_subparsers_by_group[spec.group].add_parser(spec.command)
        _configure_command_parser(command_parser, spec)

    return parser


def _build_client(args: argparse.Namespace) -> CellarClient:
    defaults = TimeoutConfig()
    timeout = TimeoutConfig(
        connect=args.timeout_connect if args.timeout_connect is not None else defaults.connect,
        read=args.timeout_read if args.timeout_read is not None else defaults.read,
        write=args.timeout_write if args.timeout_write is not None else defaults.write,
        pool=args.timeout_pool if args.timeout_pool is not None else defaults.pool,
    )

    kwargs: dict[str, Any] = {"timeout": timeout}
    if args.base_url_sparql is not None:
        kwargs["base_url_sparql"] = args.base_url_sparql
    if args.base_url_resource is not None:
        kwargs["base_url_resource"] = args.base_url_resource
    if args.retries is not None:
        kwargs["retries"] = args.retries
    return CellarClient(**kwargs)


def _build_method_kwargs(spec: CommandSpec, args: argparse.Namespace) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if spec.requires_celex:
        kwargs["celex"] = args.celex

    since = getattr(args, "since", None)
    if since is not None:
        kwargs["since"] = since

    if spec.has_resource_type:
        kwargs["resource_type"] = getattr(args, "resource_type", None)
    if spec.has_lang:
        kwargs["lang"] = args.lang
    if spec.has_limit_offset:
        kwargs["limit"] = args.limit
        kwargs["offset"] = args.offset
    if spec.has_format:
        kwargs["format"] = args.format
    if spec.list_arg_name is not None:
        kwargs[spec.list_arg_name] = getattr(args, spec.list_arg_name)
    if spec.scalar_arg_name is not None:
        kwargs[spec.scalar_arg_name] = getattr(args, spec.scalar_arg_name)
    return kwargs


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except CellarError as exc:
        return _emit_error(exc)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 1

    spec: CommandSpec = args.command_spec
    client = _build_client(args)

    try:
        method = getattr(client, spec.method)
        kwargs = _build_method_kwargs(spec, args)
        result = method(**kwargs)
        return _emit_success(result)
    except CellarError as exc:
        return _emit_error(exc)
    finally:
        client.close()


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
