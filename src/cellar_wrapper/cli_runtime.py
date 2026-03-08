"""Runtime helpers for CLI argument handling."""

from __future__ import annotations

import argparse
from typing import Any

from cellar_wrapper.http import TimeoutConfig


def positive_int(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if value < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return value


def client_kwargs_from_namespace(args: argparse.Namespace) -> dict[str, Any]:
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
    return kwargs
