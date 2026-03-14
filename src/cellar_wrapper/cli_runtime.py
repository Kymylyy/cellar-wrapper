"""Runtime helpers for CLI argument handling."""

from __future__ import annotations

import argparse
from typing import Any

from cellar_wrapper.client_config import (
    client_kwargs_from_values,
    finite_positive_float,
    positive_int,
    positive_timeout,
)


def client_kwargs_from_namespace(args: argparse.Namespace) -> dict[str, Any]:
    return client_kwargs_from_values(
        base_url_sparql=args.base_url_sparql,
        base_url_resource=args.base_url_resource,
        user_agent=args.user_agent,
        retries=args.retries,
        timeout_connect=args.timeout_connect,
        timeout_read=args.timeout_read,
        timeout_write=args.timeout_write,
        timeout_pool=args.timeout_pool,
    )


__all__ = [
    "client_kwargs_from_namespace",
    "finite_positive_float",
    "positive_int",
    "positive_timeout",
]
