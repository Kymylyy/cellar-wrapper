"""Shared client configuration parsing for CLI and MCP entrypoints."""

from __future__ import annotations

import argparse
import math
from typing import Any

from cellar_wrapper.errors import CellarValidationError
from cellar_wrapper.http import TimeoutConfig, validate_http_url


def positive_int(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if value < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return value


def finite_positive_float(raw: str) -> float:
    try:
        value = float(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a float") from exc
    try:
        return validate_finite_positive_float(value, field="value")
    except CellarValidationError as exc:
        raise argparse.ArgumentTypeError(str(exc).removeprefix("value ")) from exc


def parse_positive_int(raw: str | int, *, field_name: str) -> int:
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise CellarValidationError(f"{field_name} must be an integer: {raw!r}") from exc
    if value < 1:
        raise CellarValidationError(f"{field_name} must be >= 1")
    return value


def validate_finite_positive_float(raw: str | float, *, field: str) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise CellarValidationError(f"{field} must be a float: {raw!r}") from exc
    if not math.isfinite(value):
        raise CellarValidationError(f"{field} must be finite")
    if value <= 0:
        raise CellarValidationError(f"{field} must be > 0")
    return value


def timeout_config_from_overrides(
    *,
    connect: float | str | None = None,
    read: float | str | None = None,
    write: float | str | None = None,
    pool: float | str | None = None,
) -> TimeoutConfig:
    defaults = TimeoutConfig()
    return TimeoutConfig(
        connect=defaults.connect if connect is None else validate_finite_positive_float(connect, field="timeout.connect"),
        read=defaults.read if read is None else validate_finite_positive_float(read, field="timeout.read"),
        write=defaults.write if write is None else validate_finite_positive_float(write, field="timeout.write"),
        pool=defaults.pool if pool is None else validate_finite_positive_float(pool, field="timeout.pool"),
    )


def build_client_kwargs(
    *,
    base_url_sparql: str | None = None,
    base_url_resource: str | None = None,
    user_agent: str | None = None,
    retries: str | int | None = None,
    timeout_connect: float | str | None = None,
    timeout_read: float | str | None = None,
    timeout_write: float | str | None = None,
    timeout_pool: float | str | None = None,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "timeout": timeout_config_from_overrides(
            connect=timeout_connect,
            read=timeout_read,
            write=timeout_write,
            pool=timeout_pool,
        )
    }
    if base_url_sparql is not None:
        kwargs["base_url_sparql"] = validate_http_url(base_url_sparql, field="base_url_sparql")
    if base_url_resource is not None:
        kwargs["base_url_resource"] = validate_http_url(base_url_resource, field="base_url_resource")
    if user_agent is not None:
        kwargs["user_agent"] = user_agent
    if retries is not None:
        kwargs["retries"] = parse_positive_int(retries, field_name="retries")
    return kwargs


def client_kwargs_from_values(**kwargs: Any) -> dict[str, Any]:
    return build_client_kwargs(**kwargs)


positive_timeout = finite_positive_float

__all__ = [
    "build_client_kwargs",
    "client_kwargs_from_values",
    "finite_positive_float",
    "parse_positive_int",
    "positive_int",
    "positive_timeout",
    "timeout_config_from_overrides",
    "validate_finite_positive_float",
]
