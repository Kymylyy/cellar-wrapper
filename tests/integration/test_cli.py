from __future__ import annotations

import json

import pytest

from cellar_wrapper import cli
from cellar_wrapper.errors import CellarValidationError
from cellar_wrapper.models import ActRef


class StubClient:
    def resolve_celex(self, celex: str) -> ActRef:
        return ActRef(uri="http://publications.europa.eu/resource/cellar/act", celex=celex)

    def new_citations(self, **kwargs: object) -> None:
        raise CellarValidationError("bad since")

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
