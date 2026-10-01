#!/usr/bin/env python3
"""Execute an approved HRM lifecycle from the prebuilt source-backed plan.

The script does not analyze source or edit .bru files. It refuses mutating or
fixture-dependent execution unless the caller explicitly opts in.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
DEFAULT_PLAN = HERE.parent / "references" / "generated" / "api-execution-order.json"
DEFAULT_COLLECTION = SKILL_ROOT / "collection"
MUTATING = {"mutate", "upload", "workflow_transition", "delete", "transient_preview", "external_call"}
SECRET_RE = re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._-]{16,}|(cookie\s*:\s*)[^\n]+|((?:token|password|secret|api[_-]?key)\s*[:=]\s*)[^\s,;]+")
SENSITIVE_KEY_RE = re.compile(r"(?i)(token|password|secret|api[_-]?key|authorization|cookie|session)")


def sanitize(text: str) -> str:
    return SECRET_RE.sub(lambda m: (m.group(1) or m.group(2) or m.group(3) or "") + "<redacted>", text)


def sanitize_value(value: Any, key: str = "") -> Any:
    """Redact credentials recursively in an error response body."""
    if SENSITIVE_KEY_RE.search(key):
        return "<redacted>"
    if isinstance(value, str):
        return sanitize(value)
    if isinstance(value, list):
        return [sanitize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(name): sanitize_value(item, str(name)) for name, item in value.items()}
    return value


def load_nodes(plan_path: Path) -> list[dict[str, Any]]:
    data = json.loads(plan_path.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    if not nodes:
        raise SystemExit(f"plan has no nodes: {plan_path}")
    return nodes


def load_known_findings(plan_path: Path) -> list[dict[str, Any]]:
    """Load build-time findings without re-scanning source at runtime."""
    path = plan_path.parent / "api-constraints.yaml"
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return data.get("known_findings", [])


def dependency_closure(nodes: list[dict[str, Any]], selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {node["id"]: node for node in nodes}
    needed: set[str] = set()
    stack = [node["id"] for node in selected]
    while stack:
        node_id = stack.pop()
        if node_id in needed:
            continue
        needed.add(node_id)
        stack.extend(dep for dep in by_id.get(node_id, {}).get("depends_on", []) if dep in by_id)
    return [node for node in nodes if node["id"] in needed]


def environment_args(collection: Path, env: str | None) -> list[str]:
    """Resolve the user-facing environment value for Bruno CLI 4.x.

    The skill historically documented ``KG - local.bru``. Bruno CLI's
    ``--env`` option expects a name and appends ``.bru`` itself, so passing the
    documented filename would look for ``*.bru.bru``. Prefer ``--env-file``
    whenever the caller supplied an existing file or a file under the
    collection's ``environments`` directory.
    """
    if not env:
        return []
    candidate = Path(env).expanduser()
    if not candidate.is_absolute():
        candidate = collection / candidate
    if candidate.is_file():
        return ["--env-file", str(candidate.resolve())]
    if env.endswith(".bru"):
        candidate = collection / "environments" / env
        if candidate.is_file():
            return ["--env-file", str(candidate.resolve())]
    return ["--env", env]


def flatten_report(report_path: Path) -> list[dict[str, Any]]:
    """Flatten Bruno's iteration-wrapped JSON reporter output."""
    if not report_path.is_file():
        return []
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    entries: list[dict[str, Any]] = []
    for iteration in payload if isinstance(payload, list) else []:
        entries.extend(iteration.get("results", []))
    return entries


def report_entry_failed(entry: dict[str, Any]) -> bool:
    """Treat HTTP errors and Bruno assertion/script errors as failures.

    Bruno can leave the top-level entry status as ``pass`` when the HTTP
    exchange completed but a post-response script failed (for example, an ID
    capture script receiving HTTP 422). The lifecycle runner must not classify
    that request as passed.
    """
    if str(entry.get("status", "")).lower() in {"fail", "failed", "error"}:
        return True
    response_status = entry.get("response", {}).get("status")
    if isinstance(response_status, int) and response_status >= 400:
        return True
    for key in ("assertionResults", "testResults", "preRequestTestResults", "postResponseTestResults"):
        for result in entry.get(key, []) or []:
            if str(result.get("status", "")).lower() not in {"pass", "passed", "success"}:
                return True
    return False


def report_entry_error(entry: dict[str, Any]) -> Any:
    """Return a compact assertion/script error without persisting response bodies."""
    errors: list[Any] = []
    if entry.get("error"):
        errors.append(entry["error"])
    for key in ("assertionResults", "testResults", "preRequestTestResults", "postResponseTestResults"):
        for result in entry.get(key, []) or []:
            if str(result.get("status", "")).lower() not in {"pass", "passed", "success"}:
                errors.append({"description": result.get("description"), "error": result.get("error")})
    return errors or None


def report_entry_body(entry: dict[str, Any]) -> Any:
    """Return only the failed response body, already recursively redacted."""
    response = entry.get("response", {}) or {}
    for key in ("error_body", "data", "body", "bodyText", "rawBody"):
        if key in response and response[key] not in (None, ""):
            return sanitize_value(response[key])
    return None


def sanitize_report_file(report_path: Path) -> None:
    """Keep error bodies only; remove successful bodies and all headers in-place."""
    if not report_path.is_file():
        return
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    for iteration in payload if isinstance(payload, list) else []:
        for entry in iteration.get("results", []):
            request = entry.get("request") or {}
            request.pop("headers", None)
            request.pop("body", None)
            request.pop("data", None)
            response = entry.get("response") or {}
            response.pop("headers", None)
            if report_entry_failed(entry):
                body = report_entry_body(entry)
                for key in ("data", "body", "bodyText", "rawBody"):
                    response.pop(key, None)
                if body is not None:
                    response["error_body"] = body
            else:
                for key in ("data", "body", "bodyText", "rawBody", "error_body"):
                    response.pop(key, None)
    try:
        report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        return


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--collection", type=Path, default=DEFAULT_COLLECTION)
    parser.add_argument("--flow", help="run one named flow; required for --execute unless explicit --request paths are supplied")
    parser.add_argument(
        "--request",
        action="append",
        default=[],
        metavar="PATH_OR_ID",
        help="select one Bruno path or plan node id (repeatable); preserves the supplied order",
    )
    parser.add_argument(
        "--no-dependency-closure",
        action="store_true",
        help="execute only the explicitly selected requests; use only with a complete, reviewed lifecycle sequence",
    )
    parser.add_argument("--env", help="Bruno environment name")
    parser.add_argument("--bru", default=os.environ.get("BRU_BIN", "bru"))
    parser.add_argument("--execute", action="store_true", help="actually invoke Bruno; otherwise print the sequence")
    parser.add_argument("--allow-mutations", action="store_true", help="allow create/update/upload/workflow/delete requests")
    parser.add_argument("--allow-hardcoded-fixtures", action="store_true", help="allow requests containing hardcoded IDs or credentials")
    parser.add_argument("--allow-db-binding", action="store_true", help="confirm that the Bruno session/DB selection is configured for the target database")
    parser.add_argument("--allow-generic-session", action="store_true", help="confirm that auth=\"user\" generic routes have a persisted Odoo session cookie")
    parser.add_argument(
        "--include-error-body",
        action="store_true",
        help="retain only redacted response bodies for failed requests; successful bodies remain removed",
    )
    parser.add_argument("--include-aliases", action="store_true", help="include duplicate route aliases")
    parser.add_argument("--max-steps", type=int, default=0)
    parser.add_argument("--report-dir", type=Path, default=Path("/tmp/hrm-pack-api-test"))
    args = parser.parse_args()

    plan_path = args.plan.resolve()
    collection = args.collection.resolve()
    if not plan_path.is_file():
        raise SystemExit(f"plan not found: {plan_path}")
    if not collection.is_dir():
        raise SystemExit(f"collection not found: {collection}")
    nodes = load_nodes(plan_path)
    known_findings = load_known_findings(plan_path)
    if args.flow and args.request:
        raise SystemExit("choose either --flow or --request; do not mix the two selectors")
    if args.execute and not args.flow and not args.request:
        raise SystemExit("refusing full-collection execution: pass --flow <name> or explicit --request paths and review the generated sequence")

    available = [node for node in nodes if args.include_aliases or node.get("default_execution", True)]
    requested_nodes: list[dict[str, Any]] = []
    if args.request:
        by_path = {node["bruno_path"]: node for node in available}
        by_id = {node["id"]: node for node in available}
        missing: list[str] = []
        for key in args.request:
            node = by_path.get(key) or by_id.get(key)
            if node is None:
                missing.append(key)
            elif node not in requested_nodes:
                requested_nodes.append(node)
        if missing:
            raise SystemExit("unknown --request selector(s): " + ", ".join(missing))
        selected = requested_nodes
    else:
        selected = available
    if args.flow:
        selected = [node for node in selected if node.get("flow") == args.flow]
        if not selected:
            raise SystemExit(f"no nodes found for flow: {args.flow}")
    if not args.no_dependency_closure:
        selected = dependency_closure(nodes, selected)
    if args.request:
        # An explicit, reviewed lifecycle sequence may provide its own order. Preserve that
        # order while still placing any requested node dependencies before it.
        # With --no-dependency-closure the manifest itself is authoritative.
        if args.no_dependency_closure:
            selected = requested_nodes
        else:
            by_id = {node["id"]: node for node in selected}
            requested_ids = [node["id"] for node in requested_nodes]
            ordered: list[dict[str, Any]] = []
            visited: set[str] = set()

            def visit(node_id: str) -> None:
                if node_id in visited or node_id not in by_id:
                    return
                visited.add(node_id)
                for dependency in by_id[node_id].get("depends_on", []):
                    visit(dependency)
                ordered.append(by_id[node_id])

            for node_id in requested_ids:
                visit(node_id)
            for node in sorted(selected, key=lambda item: item["order"]):
                visit(node["id"])
            selected = ordered
    else:
        selected.sort(key=lambda node: node["order"])
    if args.max_steps:
        selected = selected[: args.max_steps]

    blocked: list[str] = []
    finding_by_scope = {item.get("scope"): item for item in known_findings}
    for node in selected:
        if node.get("operation") in MUTATING and not args.allow_mutations:
            blocked.append(f"{node['order']}: {node['bruno_path']} ({node['operation']}) requires --allow-mutations")
        if node.get("hardcoded_ids") and not args.allow_hardcoded_fixtures:
            blocked.append(f"{node['order']}: {node['bruno_path']} contains hardcoded IDs; requires --allow-hardcoded-fixtures")
        # A literal bearer token/cookie is never made safe by a generic
        # fixture override. Sanitize the .bru request instead of forwarding
        # stale credentials to another database.
        if any("hardcoded auth/cookie" in risk for risk in node.get("risks", [])):
            blocked.append(f"{node['order']}: {node['bruno_path']} contains hardcoded credential material; sanitize the request before execution")
        if args.execute and node.get("url", "").startswith("{{base_url}}") and node.get("name") != "login" and not args.allow_db_binding:
            blocked.append(f"{node['order']}: {node['bruno_path']} requires explicit DB/session binding; pass --allow-db-binding after verifying the target database")
        if args.execute and node.get("route_kind") in {"generic", "upload"} and not args.allow_generic_session:
            blocked.append(f"{node['order']}: {node['bruno_path']} uses auth=\"user\" generic routing; pass --allow-generic-session after verifying the persisted Odoo session cookie")

        # Request-scoped build findings are hard blockers, even when mutation
        # and fixture flags are supplied.
        finding = finding_by_scope.get(node["bruno_path"])
        if finding and str(finding.get("id", "")).startswith("BLOCKED-"):
            blocked.append(f"{node['order']}: {node['bruno_path']} blocked by {finding['id']}: {finding.get('action', 'review the generated constraints')}")

    print(f"plan: {plan_path}")
    print(f"collection: {collection}")
    selector = args.flow or (f"explicit ({len(args.request)} requests)" if args.request else "<not selected>")
    print("mode: lifecycle")
    print(f"flow: {selector}")
    print(f"steps: {len(selected)}")
    for node in selected:
        deps = ", ".join(node.get("depends_on", [])) or "none"
        print(f"{node['order']:03d} [{node['operation']}] {node['bruno_path']}  depends_on={deps}")
    if blocked:
        print("\nBLOCKED preflight:")
        for item in blocked:
            print(f"- {item}")
        return 2
    if not args.execute:
        print("\nDry run only. Add --execute after reviewing this sequence.")
        return 0

    print(
        "\nWARNING: execute this skill only against a disposable local/test Odoo database. "
        "Never target shared, staging, or production data."
    )

    args_env = environment_args(collection, args.env)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = args.report_dir / stamp
    run_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "plan": str(plan_path),
        "mode": "lifecycle",
        "flow": args.flow,
        "started_at": stamp,
        "steps": [],
    }
    checkpoint_path = run_dir / "checkpoint.json"
    # One Bruno process is required: its cookie jar and bru.setVar() runtime
    # variables are process-scoped. Passing all selected request paths in one
    # invocation preserves login/session and create->detail ID chaining.
    report = run_dir / "sequence.json"
    command = [
        args.bru,
        "run",
        *(node["bruno_path"] for node in selected),
        *args_env,
        "--reporter-json",
        str(report),
        "--reporter-skip-all-headers",
        "--bail",
    ]
    if not args.include_error_body:
        command.insert(command.index("--reporter-skip-all-headers"), "--reporter-skip-body")
    print(f"\nRUN sequence ({len(selected)} requests) in one Bruno process")
    try:
        completed = subprocess.run(command, cwd=collection, text=True, capture_output=True, check=False)
    except FileNotFoundError:
        print(f"ERROR: Bruno CLI not found: {args.bru}", file=sys.stderr)
        checkpoint["steps"] = [{"node": node["id"], "status": "runner_missing", "command": command} for node in selected]
        checkpoint_path.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding="utf-8")
        return 2
    (run_dir / "sequence.log").write_text(sanitize(completed.stdout + "\n" + completed.stderr), encoding="utf-8")

    report_entries = flatten_report(report)
    if args.include_error_body:
        sanitize_report_file(report)
        report_entries = flatten_report(report)
    by_filename = {
        str(entry.get("test", {}).get("filename", "")): entry
        for entry in report_entries
    }
    for node in selected:
        entry = by_filename.get(node["bruno_path"])
        if entry is None:
            status = "failed" if completed.returncode else "unknown"
            detail: dict[str, Any] = {}
        else:
            status = "failed" if report_entry_failed(entry) else str(entry.get("status", "unknown"))
            detail = {
                "http_status": entry.get("response", {}).get("status"),
                "error": report_entry_error(entry),
            }
            if args.include_error_body and report_entry_failed(entry):
                detail["error_body"] = report_entry_body(entry)
        checkpoint["steps"].append({"node": node["id"], "status": status, "report": str(report), **detail})
    checkpoint_path.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding="utf-8")
    if completed.returncode != 0:
        failed = next(
            (
                entry.get("test", {}).get("filename")
                for entry in report_entries
                if report_entry_failed(entry)
            ),
            "unknown request",
        )
        print(f"STOP: Bruno failed at {failed}; checkpoint: {checkpoint_path}", file=sys.stderr)
        return completed.returncode or 1
    checkpoint["finished_at"] = datetime.now(timezone.utc).isoformat()
    checkpoint_path.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"PASS: {len(selected)} steps; checkpoint: {checkpoint_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
