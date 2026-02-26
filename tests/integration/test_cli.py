from __future__ import annotations

import json

import pytest

from cellar_wrapper import cli
from cellar_wrapper.errors import CellarValidationError
from cellar_wrapper.models import ActRef


class StubClient:
    def __init__(self) -> None:
        self.search_by_title_calls: list[dict[str, object]] = []

    def resolve_celex(self, celex: str) -> ActRef:
        return ActRef(uri="http://publications.europa.eu/resource/cellar/act", celex=celex)

    def new_citations(self, **kwargs: object) -> None:
        raise CellarValidationError("bad since")

    def search_by_title(self, **kwargs: object) -> dict[str, object]:
        self.search_by_title_calls.append(kwargs)
        return {"items": [], "kwargs": kwargs}

    def close(self) -> None:
        return None


def test_cli_success_json(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(cli, "_build_client", lambda args: StubClient())
    exit_code = cli.run(["lookup", "resolve-celex", "--celex", "32022R2554"])
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["data"]["celex"] == "32022R2554"


def test_cli_error_json(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(cli, "_build_client", lambda args: StubClient())
    exit_code = cli.run(
        [
            "monitoring",
            "new-citations",
            "--celex",
            "32022R2554",
            "--since",
            "bad",
        ]
    )
    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["error"]["type"] == "CellarValidationError"


def test_cli_parser_error_returns_json(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli.run(["lookup", "resolve-celex"])
    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["error"]["type"] == "CellarValidationError"


def test_cli_retries_validation_returns_json(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli.run(["--retries", "0", "lookup", "resolve-celex", "--celex", "32022R2554"])
    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["error"]["type"] == "CellarValidationError"


def test_cli_rejects_since_for_get_deadlines(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli.run(
        [
            "lifecycle",
            "get-deadlines",
            "--celex",
            "32022R2554",
            "--since",
            "2025-01-01",
        ]
    )
    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["error"]["type"] == "CellarValidationError"


def test_cli_rejects_since_for_get_article_annotations(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli.run(
        [
            "case-law",
            "get-article-annotations",
            "--celex",
            "32022R2554",
            "--since",
            "2025-01-01",
        ]
    )
    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["error"]["type"] == "CellarValidationError"


def test_cli_allows_since_for_search_by_title(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    stub = StubClient()
    monkeypatch.setattr(cli, "_build_client", lambda args: stub)
    exit_code = cli.run(
        [
            "search",
            "search-by-title",
            "--keyword",
            "payment",
            "--since",
            "2025-01-01",
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert stub.search_by_title_calls[0]["since"] == "2025-01-01"
