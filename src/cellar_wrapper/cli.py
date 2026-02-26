"""Command-line interface for CELLAR wrapper."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from cellar_wrapper.client import CellarClient
from cellar_wrapper.constants import DEFAULT_LANGUAGE, DEFAULT_LIMIT, DEFAULT_OFFSET
from cellar_wrapper.errors import CellarError, CellarHTTPError, CellarRateLimitError
from cellar_wrapper.http import TimeoutConfig
from cellar_wrapper.models import ErrorPayload


@dataclass(frozen=True)
class CommandSpec:
    group: str
    command: str
    method: str
    requires_celex: bool = False
    requires_since: bool = False
    has_resource_type: bool = False
    has_lang: bool = False
    has_limit_offset: bool = False
    has_format: bool = False
    list_arg_name: str | None = None
    scalar_arg_name: str | None = None


COMMANDS: list[CommandSpec] = [
    CommandSpec("lookup", "resolve-celex", "resolve_celex", requires_celex=True),
    CommandSpec("lookup", "get-act", "get_act", requires_celex=True, has_lang=True),
    CommandSpec("lookup", "get-eurovoc", "get_eurovoc", requires_celex=True, has_limit_offset=True),
    CommandSpec(
        "lookup",
        "get-subject-matter",
        "get_subject_matter",
        requires_celex=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "lookup",
        "get-legal-basis",
        "get_legal_basis",
        requires_celex=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "lookup",
        "get-directory-codes",
        "get_directory_codes",
        requires_celex=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "lookup",
        "get-expressions",
        "get_expressions",
        requires_celex=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-amendments",
        "get_amendments",
        requires_celex=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-repeals",
        "get_repeals",
        requires_celex=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-citations",
        "get_citations",
        requires_celex=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-delegated-acts",
        "get_delegated_acts",
        requires_celex=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-completing-acts",
        "get_completing_acts",
        requires_celex=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-proposals-to-amend",
        "get_proposals_to_amend",
        requires_celex=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-adopted-act",
        "get_adopted_act",
        requires_celex=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-related-works",
        "get_related_works",
        requires_celex=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec(
        "relations",
        "get-other-relations",
        "get_other_relations",
        requires_celex=True,
        has_resource_type=True,
        has_lang=True,
        has_limit_offset=True,
    ),
    CommandSpec("lifecycle", "get-consolidated-versions", "get_consolidated_versions", requires_celex=True, has_lang=True, has_limit_offset=True),
    CommandSpec("lifecycle", "get-corrigenda", "get_corrigenda", requires_celex=True, has_lang=True, has_limit_offset=True),
    CommandSpec("lifecycle", "get-nims", "get_nims", requires_celex=True, has_lang=True, has_limit_offset=True),
    CommandSpec("lifecycle", "get-dossier", "get_dossier", requires_celex=True, has_lang=True, has_limit_offset=True),
    CommandSpec("lifecycle", "get-opinions", "get_opinions", requires_celex=True, has_lang=True, has_limit_offset=True),
    CommandSpec("lifecycle", "get-deadlines", "get_deadlines", requires_celex=True, has_limit_offset=True),
    CommandSpec("case-law", "get-cjeu-judgments", "get_cjeu_judgments", requires_celex=True, has_lang=True, has_limit_offset=True),
    CommandSpec("case-law", "get-ag-opinions", "get_ag_opinions", requires_celex=True, has_lang=True, has_limit_offset=True),
    CommandSpec("case-law", "get-preliminary-questions", "get_preliminary_questions", requires_celex=True, has_lang=True, has_limit_offset=True),
    CommandSpec("case-law", "get-national-decisions", "get_national_decisions", requires_celex=True, has_lang=True, has_limit_offset=True),
    CommandSpec("case-law", "get-article-annotations", "get_article_annotations", requires_celex=True, has_limit_offset=True),
    CommandSpec("search", "search-by-eurovoc", "search_by_eurovoc", list_arg_name="tags", has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("search", "search-by-subject-matter", "search_by_subject_matter", list_arg_name="codes", has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("search", "search-by-title", "search_by_title", scalar_arg_name="keyword", has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("search", "search-communications", "search_communications", scalar_arg_name="dg", has_lang=True, has_limit_offset=True),
    CommandSpec("search", "find-eurovoc-concept", "find_eurovoc_concept", scalar_arg_name="label", has_limit_offset=True),
    CommandSpec("monitoring", "new-citations", "new_citations", requires_celex=True, requires_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("monitoring", "new-amendments", "new_amendments", requires_celex=True, requires_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("monitoring", "new-delegated-acts", "new_delegated_acts", requires_celex=True, requires_since=True, has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("monitoring", "new-case-law", "new_case_law", requires_celex=True, requires_since=True, has_lang=True, has_limit_offset=True),
    CommandSpec("monitoring", "new-corrigenda", "new_corrigenda", requires_celex=True, requires_since=True, has_lang=True, has_limit_offset=True),
    CommandSpec("monitoring", "new-consolidated", "new_consolidated", requires_celex=True, requires_since=True, has_lang=True, has_limit_offset=True),
    CommandSpec("monitoring", "new-nims", "new_nims", requires_celex=True, requires_since=True, has_lang=True, has_limit_offset=True),
    CommandSpec("monitoring", "new-by-eurovoc", "new_by_eurovoc", requires_since=True, list_arg_name="tags", has_resource_type=True, has_lang=True, has_limit_offset=True),
    CommandSpec("download", "get-text", "get_text", requires_celex=True, has_lang=True, has_format=True),
    CommandSpec("download", "get-summary", "get_summary", requires_celex=True, has_lang=True),
]


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    return value


def _emit_success(data: Any) -> int:
    payload = {"ok": True, "data": _to_jsonable(data)}
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def _emit_error(exc: Exception) -> int:
    details: dict[str, Any] = {}
    if isinstance(exc, CellarHTTPError):
        details = {
            "status_code": exc.status_code,
            "url": exc.url,
            "body_excerpt": exc.body_excerpt,
            "details": exc.details,
        }
        if isinstance(exc, CellarRateLimitError):
            details["retry_after"] = exc.retry_after

    error = ErrorPayload(type=type(exc).__name__, message=str(exc), details=details)
    payload = {"ok": False, "error": error.model_dump(mode="json")}
    print(json.dumps(payload, ensure_ascii=False))
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cellar")
    parser.add_argument("--base-url-sparql", default=None)
    parser.add_argument("--base-url-resource", default=None)
    parser.add_argument("--retries", type=int, default=None)
    parser.add_argument("--timeout-connect", type=float, default=None)
    parser.add_argument("--timeout-read", type=float, default=None)
    parser.add_argument("--timeout-write", type=float, default=None)
    parser.add_argument("--timeout-pool", type=float, default=None)

    group_subparsers = parser.add_subparsers(dest="group", required=True)
    by_group: dict[str, argparse.ArgumentParser] = {}
    for spec in COMMANDS:
        if spec.group not in by_group:
            group_parser = group_subparsers.add_parser(spec.group)
            by_group[spec.group] = group_parser
            group_parser.set_defaults(group_name=spec.group)
            group_parser._cmd_subparsers = group_parser.add_subparsers(dest="command", required=True)  # type: ignore[attr-defined]

        command_parser = by_group[spec.group]._cmd_subparsers.add_parser(spec.command)  # type: ignore[attr-defined]
        command_parser.set_defaults(command_spec=spec)

        if spec.requires_celex:
            command_parser.add_argument("--celex", required=True)
        if spec.requires_since:
            command_parser.add_argument("--since", required=True)
        elif spec.method.startswith("get_") and spec.group in {"relations", "lifecycle", "case-law"}:
            command_parser.add_argument("--since")

        if spec.has_resource_type:
            command_parser.add_argument("--resource-type")
        if spec.has_lang:
            command_parser.add_argument("--lang", default=DEFAULT_LANGUAGE)
        if spec.has_limit_offset:
            command_parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
            command_parser.add_argument("--offset", type=int, default=DEFAULT_OFFSET)
        if spec.has_format:
            command_parser.add_argument("--format", default="pdf")
        if spec.list_arg_name is not None:
            command_parser.add_argument(f"--{spec.list_arg_name}", nargs="+", required=True)
        if spec.scalar_arg_name is not None:
            command_parser.add_argument(f"--{spec.scalar_arg_name}", required=True)

    return parser


def _build_client(args: argparse.Namespace) -> CellarClient:
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
    if args.retries is not None:
        kwargs["retries"] = args.retries
    return CellarClient(**kwargs)


def _build_method_kwargs(spec: CommandSpec, args: argparse.Namespace) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if spec.requires_celex:
        kwargs["celex"] = args.celex
    if spec.requires_since or hasattr(args, "since"):
        since = getattr(args, "since", None)
        if since is not None:
            kwargs["since"] = since

    if spec.has_resource_type:
        kwargs["resource_type"] = getattr(args, "resource_type", None)
    if spec.has_lang:
        kwargs["lang"] = args.lang
    if spec.has_limit_offset:
        kwargs["limit"] = args.limit
        kwargs["offset"] = args.offset
    if spec.has_format:
        kwargs["format"] = args.format
    if spec.list_arg_name is not None:
        kwargs[spec.list_arg_name] = getattr(args, spec.list_arg_name)
    if spec.scalar_arg_name is not None:
        kwargs[spec.scalar_arg_name] = getattr(args, spec.scalar_arg_name)
    return kwargs


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    spec: CommandSpec = args.command_spec
    client = _build_client(args)

    try:
        method = getattr(client, spec.method)
        kwargs = _build_method_kwargs(spec, args)
        result = method(**kwargs)
        return _emit_success(result)
    except (CellarError, AttributeError, ValueError, TypeError) as exc:
        return _emit_error(exc)
    finally:
        client.close()


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
