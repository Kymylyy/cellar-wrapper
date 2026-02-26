from __future__ import annotations

import os

import pytest

from cellar_wrapper.client import CellarClient

pytestmark = pytest.mark.live


@pytest.mark.skipif(os.getenv("CELLAR_LIVE") != "1", reason="Set CELLAR_LIVE=1 to run live tests")
def test_live_resolve_celex() -> None:
    client = CellarClient()
    try:
        result = client.resolve_celex("32022R2554")
        assert result.uri.startswith("http://publications.europa.eu/resource/cellar/")
    finally:
        client.close()
