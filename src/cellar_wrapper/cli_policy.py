"""CLI argument policy derived from command parameter metadata."""

from __future__ import annotations

import argparse
from typing import Any

from cellar_wrapper.cli_runtime import positive_int
from cellar_wrapper.cli_specs import CommandParameterSpec, CommandSpec


def _argparse_kwargs(param: CommandParameterSpec) -> dict[str, Any]:
    kwargs: dict[str, Any] = {"help": param.help_text}
    if param.required:
        kwargs["required"] = True
    if param.has_default:
        kwargs["default"] = param.default
    if param.choices is not None:
        kwargs["choices"] = param.choices
    if param.is_list:
        kwargs["nargs"] = "+"
    if param.kind == "limit":
        kwargs["type"] = positive_int
    elif param.kind == "offset":
        kwargs["type"] = int
    return kwargs


def configure_command_parser(command_parser: argparse.ArgumentParser, spec: CommandSpec) -> None:
    """Attach command-specific arguments based on command metadata."""
    command_parser.set_defaults(command_spec=spec)
    for param in spec.parameters:
        command_parser.add_argument(param.cli_option, **_argparse_kwargs(param))


def build_method_kwargs(spec: CommandSpec, args: argparse.Namespace) -> dict[str, Any]:
    """Map parsed CLI args to client method kwargs."""
    kwargs: dict[str, Any] = {}
    for param in spec.parameters:
        value = getattr(args, param.name)
        if value is None and param.name in {"since", "to"}:
            continue
        kwargs[param.name] = value
    return kwargs
