"""Command-line interface for CELLAR wrapper."""

from __future__ import annotations

import argparse
import json
from typing import Any, NoReturn

from cellar_wrapper.cli_policy import build_method_kwargs, configure_command_parser
from cellar_wrapper.cli_specs import COMMANDS, CommandSpec
from cellar_wrapper.client import CellarClient
from cellar_wrapper.errors import (
    CellarError,
    CellarHTTPError,
    CellarInternalError,
    CellarNotFoundError,
    CellarParseError,
    CellarRateLimitError,
    CellarSPARQLError,
    CellarValidationError,
)
from cellar_wrapper.http import TimeoutConfig
from cellar_wrapper.models import ErrorPayload
from cellar_wrapper.serialization import to_jsonable


class JsonArgumentParser(argparse.ArgumentParser):
    """ArgumentParser variant that surfaces validation errors as exceptions."""

    def error(self, message: str) -> NoReturn:  # pragma: no cover - exercised via run()
        raise CellarValidationError(message)


def _emit_success(data: Any) -> int:
    payload = {"ok": True, "data": to_jsonable(data)}
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
    elif isinstance(exc, CellarNotFoundError):
        details = {"details": exc.details}
    elif isinstance(exc, CellarParseError):
        details = {"details": exc.details}
    elif isinstance(exc, CellarInternalError):
        details = exc.details

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
    parser.add_argument("--base-url-sparql", default=None, help="Override SPARQL endpoint URL.")
    parser.add_argument("--base-url-resource", default=None, help="Override resource base URL.")
    parser.add_argument("--user-agent", default=None, help="Override HTTP User-Agent header.")
    parser.add_argument("--retries", type=_positive_int, default=None, help="Total retry attempts.")
    parser.add_argument("--timeout-connect", type=float, default=None, help="Connection timeout (seconds).")
    parser.add_argument("--timeout-read", type=float, default=None, help="Read timeout (seconds).")
    parser.add_argument("--timeout-write", type=float, default=None, help="Write timeout (seconds).")
    parser.add_argument("--timeout-pool", type=float, default=None, help="Pool timeout (seconds).")


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
        configure_command_parser(command_parser, spec)

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
    if args.user_agent is not None:
        kwargs["user_agent"] = args.user_agent
    if args.retries is not None:
        kwargs["retries"] = args.retries
    return CellarClient(**kwargs)


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except CellarError as exc:
        return _emit_error(exc)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 1

    spec: CommandSpec = args.command_spec
    client: CellarClient | None = None

    try:
        client = _build_client(args)
        method = getattr(client, spec.method)
        kwargs = build_method_kwargs(spec, args)
        result = method(**kwargs)
        return _emit_success(result)
    except CellarError as exc:
        return _emit_error(exc)
    except Exception as exc:  # pragma: no cover - guarded via integration test
        internal_error = CellarInternalError(
            "Unexpected internal error",
            details={"original_type": type(exc).__name__},
        )
        return _emit_error(internal_error)
    finally:
        if client is not None:
            client.close()


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
