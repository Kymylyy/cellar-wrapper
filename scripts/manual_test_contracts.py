#!/usr/bin/env python3
"""Run manual contract checks and generate JSON + HTML reports."""

from __future__ import annotations

import argparse
import html
import inspect
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cellar_wrapper.cli_specs import COMMANDS
from cellar_wrapper.client import CellarClient
from cellar_wrapper.serialization import to_jsonable

DEFAULT_REPORT_NAME = "contract_methods_manual_test_report"
DEFAULT_OUTPUT_ROOT = "docs/manual_test"
DEFAULT_PROFILES_FILE = Path("docs/manual_test/kwargs_profiles.json")
DEFAULT_RUNS = 2
DEFAULT_WORKERS = 8
OUTPUT_PREVIEW_LIMIT = 3000

REQUIRED_PROFILE_FIELDS = {"name", "required", "optional"}
REQUIRED_ARGS_FIELDS = {"celex", "since", "tags", "codes", "keyword", "dg", "label"}

KWARGS_PROFILES: tuple[dict[str, Any], ...] = ()
KWARGS_PROFILES_SOURCE = str(DEFAULT_PROFILES_FILE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run manual checks for all public contract methods and generate "
            "JSON + HTML reports."
        )
    )
    parser.add_argument(
        "--output-root",
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Folder for run subfolders (default: {DEFAULT_OUTPUT_ROOT}).",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional run id. Default is UTC timestamp YYYYMMDD_HHMMSS.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=DEFAULT_RUNS,
        help=(
            f"How many calls per method (default: {DEFAULT_RUNS}). "
            "Attempt kwargs cycle through configured profiles."
        ),
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Parallel method workers (default: {DEFAULT_WORKERS}).",
    )
    parser.add_argument(
        "--methods",
        nargs="*",
        default=None,
        help="Optional explicit method list. If omitted, all public methods are used.",
    )
    parser.add_argument(
        "--profiles-file",
        default=str(DEFAULT_PROFILES_FILE),
        help=f"JSON file with kwargs profiles (default: {DEFAULT_PROFILES_FILE}).",
    )
    parser.add_argument(
        "--from-json",
        default=None,
        help="Skip execution and render HTML from an existing report JSON path.",
    )
    parser.add_argument(
        "--html-out",
        default=None,
        help="Custom HTML output path (works with --from-json).",
    )
    return parser.parse_args()


def discover_methods() -> list[str]:
    return sorted({spec.method for spec in COMMANDS})


def load_kwargs_profiles(path: Path) -> tuple[dict[str, Any], ...]:
    if not path.exists():
        raise SystemExit(f"Profiles file not found: {path}")

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in profiles file {path}: {exc}") from exc

    if not isinstance(raw, list) or not raw:
        raise SystemExit(f"Profiles file must contain a non-empty JSON array: {path}")

    validated_profiles: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    for index, profile in enumerate(raw):
        if not isinstance(profile, dict):
            raise SystemExit(f"Profile #{index + 1} in {path} is not a JSON object")

        missing_fields = REQUIRED_PROFILE_FIELDS - set(profile.keys())
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise SystemExit(f"Profile #{index + 1} in {path} is missing fields: {missing}")

        name = profile["name"]
        required_args = profile["required"]
        optional_args = profile["optional"]
        if not isinstance(name, str) or not name.strip():
            raise SystemExit(f"Profile #{index + 1} in {path} has invalid 'name'")
        if name in seen_names:
            raise SystemExit(f"Duplicate profile name in {path}: {name}")
        if not isinstance(required_args, dict):
            raise SystemExit(f"Profile '{name}' in {path} has invalid 'required'")
        if not isinstance(optional_args, dict):
            raise SystemExit(f"Profile '{name}' in {path} has invalid 'optional'")

        missing_required_args = REQUIRED_ARGS_FIELDS - set(required_args.keys())
        if missing_required_args:
            missing = ", ".join(sorted(missing_required_args))
            raise SystemExit(f"Profile '{name}' in {path} is missing required args: {missing}")

        seen_names.add(name)
        validated_profiles.append(profile)

    return tuple(validated_profiles)


def build_method_kwargs(
    method_name: str,
    *,
    required_args: dict[str, Any],
    optional_args: dict[str, Any],
) -> dict[str, Any]:
    signature = inspect.signature(getattr(CellarClient, method_name))
    kwargs: dict[str, Any] = {}
    for parameter in signature.parameters.values():
        if parameter.name == "self":
            continue
        if parameter.default is inspect.Signature.empty:
            kwargs[parameter.name] = required_args[parameter.name]
        elif parameter.name in optional_args:
            kwargs[parameter.name] = optional_args[parameter.name]
    return kwargs


def kwargs_profile_for_attempt(attempt_index: int) -> dict[str, Any]:
    if not KWARGS_PROFILES:
        raise RuntimeError("No kwargs profiles loaded")
    return KWARGS_PROFILES[attempt_index % len(KWARGS_PROFILES)]


def sanitize_output(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            if key == "content_base64" and isinstance(item, str):
                sanitized[key] = "[omitted]"
                sanitized["content_base64_length"] = len(item)
                sanitized["content_base64_preview"] = item[:120]
                continue
            sanitized[key] = sanitize_output(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_output(item) for item in value]
    return value


def summarize_output(value: Any) -> dict[str, Any]:
    text = json.dumps(value, ensure_ascii=False)
    return {
        "preview": text[:OUTPUT_PREVIEW_LIMIT],
        "size_chars": len(text),
        "truncated": len(text) > OUTPUT_PREVIEW_LIMIT,
    }


def run_single_method(method_name: str, runs: int) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    profile_names_used: list[str] = []
    client = CellarClient()
    try:
        for attempt_index in range(runs):
            attempt = attempt_index + 1
            profile = kwargs_profile_for_attempt(attempt_index)
            kwargs = build_method_kwargs(
                method_name,
                required_args=profile["required"],
                optional_args=profile["optional"],
            )
            profile_names_used.append(profile["name"])
            started = time.perf_counter()
            try:
                response = getattr(client, method_name)(**kwargs)
                elapsed_ms = round((time.perf_counter() - started) * 1000.0, 3)
                output = sanitize_output(to_jsonable(response))
                attempts.append(
                    {
                        "attempt": attempt,
                        "kwargs_profile": profile["name"],
                        "kwargs": kwargs,
                        "ok": True,
                        "elapsed_ms": elapsed_ms,
                        "output": output,
                        "output_summary": summarize_output(output),
                    }
                )
            except Exception as exc:  # noqa: BLE001
                elapsed_ms = round((time.perf_counter() - started) * 1000.0, 3)
                attempts.append(
                    {
                        "attempt": attempt,
                        "kwargs_profile": profile["name"],
                        "kwargs": kwargs,
                        "ok": False,
                        "elapsed_ms": elapsed_ms,
                        "error": {
                            "type": type(exc).__name__,
                            "message": str(exc),
                        },
                    }
                )
    finally:
        client.close()

    ok_times = [attempt["elapsed_ms"] for attempt in attempts if attempt["ok"]]
    return {
        "method": method_name,
        "kwargs_profiles_used": sorted(set(profile_names_used)),
        "runs": attempts,
        "summary": {
            "ok_runs": len(ok_times),
            "error_runs": len(attempts) - len(ok_times),
            "avg_elapsed_ms_ok": round(sum(ok_times) / len(ok_times), 3) if ok_times else None,
            "min_elapsed_ms_ok": min(ok_times) if ok_times else None,
            "max_elapsed_ms_ok": max(ok_times) if ok_times else None,
        },
    }


def render_html_report(report: dict[str, Any]) -> str:
    summary = report["summary"]
    methods_html: list[str] = []
    for item in report["results"]:
        method_name = html.escape(item["method"])
        run_rows: list[str] = []
        for run in item["runs"]:
            status = "OK" if run["ok"] else "ERROR"
            status_class = "ok" if run["ok"] else "error"
            elapsed = html.escape(f"{run['elapsed_ms']} ms")
            run_profile = html.escape(run.get("kwargs_profile", "legacy"))
            run_kwargs = run.get("kwargs", item.get("kwargs", {}))
            run_kwargs_json = html.escape(json.dumps(run_kwargs, ensure_ascii=False, indent=2))
            if run["ok"]:
                legacy_output = run.get("output")
                output_summary = run.get("output_summary")

                if output_summary is None and isinstance(legacy_output, dict):
                    if {"preview", "size_chars", "truncated"} <= set(legacy_output.keys()):
                        output_summary = legacy_output
                        full_output = None
                    else:
                        full_output = legacy_output
                else:
                    full_output = run.get("output")

                if output_summary is None:
                    output_summary = summarize_output(full_output)

                output_preview = html.escape(output_summary["preview"])
                if full_output is None:
                    content = (
                        "<p class='note'>Pełny output niedostępny w starszym formacie raportu.</p>"
                        f"<pre>{output_preview}</pre>"
                    )
                else:
                    output_json = html.escape(json.dumps(full_output, ensure_ascii=False, indent=2))
                    content = f"<pre>{output_json}</pre>"
            else:
                error_type = html.escape(run["error"]["type"])
                error_msg = html.escape(run["error"]["message"])
                content = f"<pre>{error_type}: {error_msg}</pre>"
            run_rows.append(
                "<tr>"
                f"<td>{run['attempt']}</td>"
                f"<td>{run_profile}</td>"
                f"<td class='{status_class}'>{status}</td>"
                f"<td>{elapsed}</td>"
                f"<td><pre>{run_kwargs_json}</pre></td>"
                f"<td>{content}</td>"
                "</tr>"
            )

        methods_html.append(
            "<section class='method'>"
            f"<h2 id='{method_name}'>{method_name}</h2>"
            "<div class='method-summary'>"
            f"ok_runs={item['summary']['ok_runs']} | error_runs={item['summary']['error_runs']}"
            "</div>"
            "<table>"
            "<thead><tr><th>Attempt</th><th>Profile</th><th>Status</th><th>Elapsed</th><th>Kwargs</th><th>Output/Error</th></tr></thead>"
            f"<tbody>{''.join(run_rows)}</tbody>"
            "</table>"
            "</section>"
        )

    failures_html = []
    for failed in summary["methods_with_failures"]:
        method = html.escape(failed["method"])
        details = "<br/>".join(
            html.escape(f"attempt {error['attempt']}: {error['type']} - {error['message']}")
            for error in failed["errors"]
        )
        failures_html.append(f"<li><b>{method}</b><br/>{details}</li>")
    failure_block = "<ul>" + "".join(failures_html) + "</ul>" if failures_html else "<p>Brak błędów.</p>"

    summary_json = html.escape(json.dumps(summary, ensure_ascii=False, indent=2))
    return f"""<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Manual Contract Test Report</title>
  <style>
    body {{
      margin: 0;
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
      background: linear-gradient(180deg, #f5f8ff 0%, #ffffff 35%, #eef4f7 100%);
      color: #14202e;
    }}
    main {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 24px;
    }}
    h1, h2 {{
      margin: 0 0 12px 0;
    }}
    .meta {{
      background: #ffffffcc;
      border: 1px solid #d8e2ef;
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 16px;
    }}
    pre {{
      white-space: pre-wrap;
      word-wrap: break-word;
      background: #0f1622;
      color: #d6e4ff;
      padding: 12px;
      border-radius: 8px;
      overflow-x: auto;
      margin: 8px 0 0 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
      background: #fff;
      border: 1px solid #d8e2ef;
    }}
    th, td {{
      text-align: left;
      vertical-align: top;
      padding: 10px;
      border-bottom: 1px solid #e3eaf4;
    }}
    th {{
      background: #eff5ff;
    }}
    .method {{
      margin-top: 20px;
      padding: 16px;
      border: 1px solid #d8e2ef;
      border-radius: 12px;
      background: #ffffffdb;
    }}
    .method-summary {{
      font-size: 14px;
      font-weight: 600;
      color: #31445f;
      margin-bottom: 8px;
    }}
    .note {{
      margin: 0;
      color: #5f6f84;
      font-size: 13px;
    }}
    .ok {{
      color: #0b6b36;
      font-weight: 700;
    }}
    .error {{
      color: #9c1c1c;
      font-weight: 700;
    }}
  </style>
</head>
<body>
<main>
  <h1>Manual Contract Test Report</h1>
  <section class="meta">
    <h2>Summary</h2>
    <pre>{summary_json}</pre>
    <h2>Failures</h2>
    {failure_block}
  </section>
  {"".join(methods_html)}
</main>
</body>
</html>
"""


def build_final_report(
    *,
    run_id: str,
    output_root: Path,
    methods: list[str],
    workers: int,
    runs: int,
    started_unix: float,
    finished_unix: float,
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    total_methods = len(results)
    total_runs = sum(len(item["runs"]) for item in results)
    runs_ok = sum(1 for item in results for run in item["runs"] if run["ok"])
    runs_failed = total_runs - runs_ok

    methods_with_failures = []
    ok_elapsed = []
    for item in results:
        method_errors = []
        for run in item["runs"]:
            if run["ok"]:
                ok_elapsed.append(run["elapsed_ms"])
            else:
                method_errors.append(
                    {
                        "attempt": run["attempt"],
                        "type": run["error"]["type"],
                        "message": run["error"]["message"],
                    }
                )
        if method_errors:
            methods_with_failures.append(
                {
                    "method": item["method"],
                    "failed_runs": len(method_errors),
                    "errors": method_errors,
                }
            )

    return {
        "meta": {
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "run_id": run_id,
            "output_root": str(output_root),
            "workers": workers,
            "runs_per_method": runs,
            "kwargs_profiles_source": KWARGS_PROFILES_SOURCE,
            "kwargs_profiles": [profile["name"] for profile in KWARGS_PROFILES],
            "methods_requested": methods,
            "started_unix": started_unix,
            "ended_unix": finished_unix,
            "duration_s": round(finished_unix - started_unix, 3),
        },
        "summary": {
            "methods_total": total_methods,
            "runs_per_method": runs,
            "runs_total": total_runs,
            "runs_ok": runs_ok,
            "runs_failed": runs_failed,
            "methods_with_failures_count": len(methods_with_failures),
            "methods_with_failures": methods_with_failures,
            "elapsed_ms_ok": {
                "avg": round(sum(ok_elapsed) / len(ok_elapsed), 3) if ok_elapsed else None,
                "min": min(ok_elapsed) if ok_elapsed else None,
                "max": max(ok_elapsed) if ok_elapsed else None,
            },
        },
        "results": results,
    }


def execute_report(
    *,
    output_root: Path,
    run_id: str,
    methods: list[str],
    workers: int,
    runs: int,
) -> tuple[Path, Path]:
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    started_unix = time.time()
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(run_single_method, method, runs): method for method in methods}
        for future in as_completed(futures):
            method = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:  # noqa: BLE001
                results.append(
                    {
                        "method": method,
                        "kwargs": {},
                        "runs": [],
                        "summary": {
                            "ok_runs": 0,
                            "error_runs": runs,
                            "avg_elapsed_ms_ok": None,
                            "min_elapsed_ms_ok": None,
                            "max_elapsed_ms_ok": None,
                        },
                        "execution_error": {
                            "type": type(exc).__name__,
                            "message": str(exc),
                        },
                    }
                )
    finished_unix = time.time()
    results.sort(key=lambda item: item["method"])

    report = build_final_report(
        run_id=run_id,
        output_root=output_root,
        methods=methods,
        workers=workers,
        runs=runs,
        started_unix=started_unix,
        finished_unix=finished_unix,
        results=results,
    )

    report_json_path = run_dir / f"{DEFAULT_REPORT_NAME}.json"
    report_html_path = run_dir / f"{DEFAULT_REPORT_NAME}.html"
    report_json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report_html_path.write_text(render_html_report(report), encoding="utf-8")
    return report_json_path, report_html_path


def render_from_json(existing_json_path: Path, html_out: Path | None) -> Path:
    report = json.loads(existing_json_path.read_text(encoding="utf-8"))
    output_path = html_out or existing_json_path.with_suffix(".html")
    output_path.write_text(render_html_report(report), encoding="utf-8")
    return output_path


def main() -> int:
    global KWARGS_PROFILES
    global KWARGS_PROFILES_SOURCE

    args = parse_args()
    if args.runs < 1:
        raise SystemExit("--runs must be >= 1")
    if args.workers < 1:
        raise SystemExit("--workers must be >= 1")

    if args.from_json:
        json_path = Path(args.from_json)
        html_path = render_from_json(json_path, Path(args.html_out) if args.html_out else None)
        print(f"Rendered HTML: {html_path}")
        return 0

    profiles_path = Path(args.profiles_file)
    KWARGS_PROFILES = load_kwargs_profiles(profiles_path)
    KWARGS_PROFILES_SOURCE = str(profiles_path)

    methods = args.methods if args.methods else discover_methods()
    run_id = args.run_id or datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    output_root = Path(args.output_root)

    report_json_path, report_html_path = execute_report(
        output_root=output_root,
        run_id=run_id,
        methods=methods,
        workers=args.workers,
        runs=args.runs,
    )

    print(f"Report JSON: {report_json_path}")
    print(f"Report HTML: {report_html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
