"""CLI argument policy derived from CommandSpec metadata."""

from __future__ import annotations

import argparse
from typing import Any

from cellar_wrapper.cli_specs import CommandSpec
from cellar_wrapper.constants import DEFAULT_LANGUAGE, DEFAULT_LIMIT, DEFAULT_OFFSET

_LIST_ARG_HELP: dict[str, str] = {
    "tags": "One or more EuroVoc tags.",
    "codes": "One or more subject-matter codes.",
}

_SCALAR_ARG_HELP: dict[str, str] = {
    "keyword": "Title keyword to search.",
    "dg": "Directorate-General code (for example FISMA).",
    "label": "EuroVoc label to match.",
}


def _list_arg_help(arg_name: str) -> str:
    return _LIST_ARG_HELP.get(arg_name, f"One or more values for {arg_name}.")


def _scalar_arg_help(arg_name: str) -> str:
    return _SCALAR_ARG_HELP.get(arg_name, f"Value for {arg_name}.")


def configure_command_parser(command_parser: argparse.ArgumentParser, spec: CommandSpec) -> None:
    """Attach command-specific arguments based on a command spec."""
    command_parser.set_defaults(command_spec=spec)

    if spec.requires_celex:
        command_parser.add_argument("--celex", required=True, help="CELEX identifier.")
    if spec.requires_since:
        command_parser.add_argument("--since", required=True, help="Include items from this date/time.")
    elif spec.has_since:
        command_parser.add_argument("--since", help="Optional lower date/time bound.")

    if spec.has_resource_type:
        command_parser.add_argument("--resource-type", help="Filter by CELLAR resource type token.")
    if spec.has_lang:
        command_parser.add_argument("--lang", default=DEFAULT_LANGUAGE, help="Language code.")
    if spec.has_limit_offset:
        command_parser.add_argument(
            "--limit",
            type=int,
            default=DEFAULT_LIMIT,
            help="Maximum number of items to return.",
        )
        command_parser.add_argument(
            "--offset",
            type=int,
            default=DEFAULT_OFFSET,
            help="Number of items to skip before returning results.",
        )
    if spec.has_format:
        command_parser.add_argument("--format", default="pdf", help="Document format (for example pdf).")
    if spec.list_arg_name is not None:
        command_parser.add_argument(
            f"--{spec.list_arg_name}",
            nargs="+",
            required=True,
            help=_list_arg_help(spec.list_arg_name),
        )
    if spec.scalar_arg_name is not None:
        command_parser.add_argument(
            f"--{spec.scalar_arg_name}",
            required=True,
            help=_scalar_arg_help(spec.scalar_arg_name),
        )


def build_method_kwargs(spec: CommandSpec, args: argparse.Namespace) -> dict[str, Any]:
    """Map parsed CLI args to client method kwargs."""
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
