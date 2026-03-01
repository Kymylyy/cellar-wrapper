"""Shared JSON-serialization helpers for CLI and MCP surfaces."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel


def to_jsonable(value: Any) -> Any:
    """Convert wrapper payloads into JSON-serializable structures."""
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, tuple | set | list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    return value
