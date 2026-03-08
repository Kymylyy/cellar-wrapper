"""Package version helpers."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

_FALLBACK_VERSION = "0.1.0"


def _detect_version() -> str:
    try:
        return version("cellar-wrapper")
    except PackageNotFoundError:
        return _FALLBACK_VERSION


__version__ = _detect_version()
