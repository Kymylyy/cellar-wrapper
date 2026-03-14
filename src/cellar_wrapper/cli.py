"""Command-line interface for CELLAR wrapper."""

from __future__ import annotations

import argparse
import json
from typing import Any, NoReturn

from cellar_wrapper.cli_policy import build_method_kwargs, configure_command_parser
from cellar_wrapper.cli_runtime import (
    client_kwargs_from_namespace,
    finite_positive_float,
    positive_int,
)
from cellar_wrapper.cli_specs import COMMANDS, CommandSpec
from cellar_wrapper.client import CellarClient
from cellar_wrapper.error_serialization import cellar_error_details
from cellar_wrapper.errors import (
    CellarError,
    CellarInternalError,
    CellarValidationError,
)
from cellar_wrapper.models import ErrorPayload
from cellar_wrapper.serialization import to_jsonable
from cellar_wrapper.version import __version__


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
    if isinstance(exc, CellarError):
        details = cellar_error_details(exc)

    error = ErrorPayload(type=type(exc).__name__, message=str(exc), details=details)
    payload = {"ok": False, "error": error.model_dump(mode="json")}
    print(json.dumps(payload, ensure_ascii=False))
    return 1


def _add_global_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--base-url-sparql", default=None, help="Override SPARQL endpoint URL.")
    parser.add_argument("--base-url-resource", default=None, help="Override resource base URL.")
    parser.add_argument("--user-agent", default=None, help="Override HTTP User-Agent header.")
    parser.add_argument("--retries", type=positive_int, default=None, help="Total retry attempts.")
    parser.add_argument(
        "--timeout-connect",
        type=finite_positive_float,
        default=None,
        help="Connection timeout (seconds).",
    )
    parser.add_argument(
        "--timeout-read",
        type=finite_positive_float,
        default=None,
        help="Read timeout (seconds).",
    )
    parser.add_argument(
        "--timeout-write",
        type=finite_positive_float,
        default=None,
        help="Write timeout (seconds).",
    )
    parser.add_argument(
        "--timeout-pool",
        type=finite_positive_float,
        default=None,
        help="Pool timeout (seconds).",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(prog="cellar")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    _add_global_args(parser)

    group_subparsers = parser.add_subparsers(dest="group", required=True)
    command_subparsers_by_group: dict[str, Any] = {}

    for spec in COMMANDS:
        if spec.group not in command_subparsers_by_group:
            group_parser = group_subparsers.add_parser(
                spec.group,
                help=f"{spec.group} commands",
                description=f"{spec.group} commands",
            )
            command_subparsers_by_group[spec.group] = group_parser.add_subparsers(
                dest="command", required=True
            )

        command_parser = command_subparsers_by_group[spec.group].add_parser(
            spec.command,
            help=spec.description,
            description=spec.description,
        )
        configure_command_parser(command_parser, spec)

    return parser


def _build_client(args: argparse.Namespace) -> CellarClient:
    return CellarClient(**client_kwargs_from_namespace(args))


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
