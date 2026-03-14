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


@pytest.mark.skipif(os.getenv("CELLAR_LIVE") != "1", reason="Set CELLAR_LIVE=1 to run live tests")
def test_live_search_by_title_filtered_resource_types_do_not_leak_sibling_types() -> None:
    client = CellarClient()
    try:
        result = client.search_by_title(
            "crypto-assets",
            since="2024-01-01",
            resource_types=["PUB_GEN"],
            lang="eng",
            limit=10,
        )
    finally:
        client.close()

    assert result.returned_count >= 1
    assert all(
        item.resource_type is not None
        and item.resource_type.endswith("/PUB_GEN")
        for item in result.items
    )


@pytest.mark.skipif(os.getenv("CELLAR_LIVE") != "1", reason="Set CELLAR_LIVE=1 to run live tests")
def test_live_new_by_eurovoc_accepts_multiple_resource_types() -> None:
    client = CellarClient()
    try:
        result = client.new_by_eurovoc(
            ["financial services"],
            since="2025-01-01",
            resource_types=["PROP_REG", "PROP_DIR"],
            lang="eng",
            limit=10,
        )
    finally:
        client.close()

    assert result.returned_count >= 1
    returned_types = {item.resource_type for item in result.items}
    assert returned_types
    assert all(
        resource_type is not None
        and resource_type.endswith(("/PROP_REG", "/PROP_DIR"))
        for resource_type in returned_types
    )
    assert any(resource_type is not None and resource_type.endswith("/PROP_REG") for resource_type in returned_types)
    assert any(resource_type is not None and resource_type.endswith("/PROP_DIR") for resource_type in returned_types)


@pytest.mark.skipif(os.getenv("CELLAR_LIVE") != "1", reason="Set CELLAR_LIVE=1 to run live tests")
def test_live_new_amendments_accepts_multiple_resource_types() -> None:
    client = CellarClient()
    try:
        result = client.new_amendments(
            "32015L2366",
            since="2022-12-01",
            resource_types=["DIR", "REG"],
            lang="eng",
            limit=10,
        )
    finally:
        client.close()

    assert result.returned_count >= 1
    returned_types = {item.resource_type for item in result.items}
    assert all(
        resource_type is not None
        and resource_type.endswith(("/DIR", "/REG"))
        for resource_type in returned_types
    )
    assert any(resource_type is not None and resource_type.endswith("/DIR") for resource_type in returned_types)
    assert any(resource_type is not None and resource_type.endswith("/REG") for resource_type in returned_types)
